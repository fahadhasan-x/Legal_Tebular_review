"""
Document Endpoints
Handles document upload, retrieval, and management
"""
from typing import List
from uuid import UUID
from pathlib import Path
import aiofiles

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.config import settings
from app.db.session import get_db
from app.models import Document, Project, UploadStatus, ProjectStatus
from app.schemas import DocumentResponse, DocumentDetail, TaskStatusResponse
from app.workers.tasks import parse_document_task

logger = structlog.get_logger(__name__)
router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================

def validate_file_type(filename: str) -> str:
    """
    Validate file extension and return file type
    
    Args:
        filename: Name of uploaded file
        
    Returns:
        str: File extension (e.g., '.pdf')
        
    Raises:
        HTTPException: If file type is not allowed
    """
    file_ext = Path(filename).suffix.lower()
    
    if file_ext not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file_ext}' not allowed. Supported types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
        )
    
    return file_ext


async def save_upload_file(upload_file: UploadFile, file_path: Path) -> int:
    """
    Save uploaded file to disk
    
    Args:
        upload_file: FastAPI UploadFile object
        file_path: Destination path
        
    Returns:
        int: File size in bytes
        
    Raises:
        HTTPException: If file exceeds max size
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await upload_file.read(chunk_size):
                file_size += len(chunk)
                
                # Check file size limit
                if file_size > settings.MAX_UPLOAD_SIZE:
                    # Delete partially written file
                    file_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
                    )
                
                await f.write(chunk)
    
    except Exception as e:
        # Clean up on error
        file_path.unlink(missing_ok=True)
        logger.error("file_save_failed", filename=upload_file.filename, error=str(e))
        raise
    
    return file_size


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/projects/{project_id}/documents/upload", 
             response_model=DocumentResponse,
             status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a document to a project
    
    - **project_id**: UUID of the project
    - **file**: Document file (PDF, DOCX, HTML, or TXT)
    
    Returns:
        DocumentResponse with upload status and metadata
        
    Process:
        1. Validate file type and size
        2. Save file to disk
        3. Create database record
        4. Trigger async parsing task
    """
    logger.info("document_upload_started", project_id=str(project_id), filename=file.filename)
    
    # Validate project exists and is active
    project_result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.status == ProjectStatus.ACTIVE
        )
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active project with ID {project_id} not found"
        )
    
    # Validate file type
    file_ext = validate_file_type(file.filename)
    
    # Generate unique file path
    document_id = UUID(int=0)  # Temporary, will be replaced
    file_path = Path(settings.UPLOAD_DIR) / str(project_id) / f"{document_id}_{file.filename}"
    
    # Save file
    try:
        file_size = await save_upload_file(file, file_path)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("unexpected_upload_error", filename=file.filename, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file"
        )
    
    # Create document record
    document = Document(
        project_id=project_id,
        filename=file.filename,
        file_type=file_ext,
        file_size=file_size,
        file_path=str(file_path),
        upload_status=UploadStatus.UPLOADED,
        file_metadata={
            "original_filename": file.filename,
            "content_type": file.content_type
        }
    )
    
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    # Update file path with actual document ID
    new_file_path = Path(settings.UPLOAD_DIR) / str(project_id) / f"{document.id}_{file.filename}"
    file_path.rename(new_file_path)
    document.file_path = str(new_file_path)
    await db.commit()
    await db.refresh(document)
    
    logger.info("document_uploaded", document_id=str(document.id), file_size=file_size)
    
    # Trigger async parsing task
    try:
        task = parse_document_task.delay(str(document.id))
        logger.info("parsing_task_queued", document_id=str(document.id), task_id=task.id)
    except Exception as e:
        logger.error("task_queue_failed", document_id=str(document.id), error=str(e))
        # Don't fail the upload if task queueing fails
    
    return document


@router.get("/projects/{project_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    project_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    List all documents in a project
    
    - **project_id**: UUID of the project
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    # Verify project exists
    project_result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    # Get documents
    result = await db.execute(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(min(limit, settings.MAX_PAGE_SIZE))
    )
    
    documents = result.scalars().all()
    return documents


@router.get("/documents/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a document
    
    - **document_id**: UUID of the document
    """
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Create response with preview
    response_data = {
        **{k: v for k, v in document.__dict__.items() if not k.startswith('_')},
        "parsed_text_preview": document.parsed_text[:500] if document.parsed_text else None,
        "metadata": document.file_metadata
    }
    
    # Get extraction status if exists
    from app.models import ExtractedRecord
    extraction_result = await db.execute(
        select(ExtractedRecord)
        .where(ExtractedRecord.document_id == document_id)
        .order_by(ExtractedRecord.created_at.desc())
        .limit(1)
    )
    extraction = extraction_result.scalar_one_or_none()
    if extraction:
        response_data["extraction_status"] = extraction.extraction_status
    
    return response_data


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a document and its associated file
    
    - **document_id**: UUID of the document
    """
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Delete physical file
    try:
        file_path = Path(document.file_path)
        file_path.unlink(missing_ok=True)
        logger.info("file_deleted", document_id=str(document_id), file_path=str(file_path))
    except Exception as e:
        logger.error("file_deletion_failed", document_id=str(document_id), error=str(e))
        # Continue with database deletion even if file deletion fails
    
    # Delete database record (cascades to extracted_records and review_records)
    await db.delete(document)
    await db.commit()
    
    logger.info("document_deleted", document_id=str(document_id))
    return None


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Download the original document file
    
    - **document_id**: UUID of the document
    """
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    file_path = Path(document.file_path)
    if not file_path.exists():
        logger.error("file_not_found", document_id=str(document_id), file_path=str(file_path))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found on disk"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=document.filename,
        media_type="application/octet-stream"
    )
