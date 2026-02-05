"""
Extraction Endpoints
Trigger and manage AI extraction tasks
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.db.session import get_db
from app.models import Document, ExtractedRecord, UploadStatus, Project
from app.schemas import (
    ExtractionRequest,
    ExtractedRecordResponse,
    TaskStatusResponse
)
from app.workers.tasks import extract_document_task

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/documents/{document_id}/extract", 
             response_model=TaskStatusResponse,
             status_code=status.HTTP_202_ACCEPTED)
async def trigger_extraction(
    document_id: UUID,
    extraction_request: ExtractionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger AI extraction for a document
    
    - **document_id**: UUID of the document
    - **field_template_id**: Field template to use for extraction
    - **force_reprocess**: Re-extract even if already extracted
    
    Returns:
        Task status with task_id for tracking
    """
    logger.info("extraction_trigger_requested", 
               document_id=str(document_id),
               template_id=str(extraction_request.field_template_id))
    
    # Verify document exists and is parsed
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    if document.upload_status != UploadStatus.PARSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document must be parsed before extraction. Current status: {document.upload_status.value}"
        )
    
    # Check if already extracted
    if not extraction_request.force_reprocess:
        existing_result = await db.execute(
            select(ExtractedRecord).where(
                ExtractedRecord.document_id == document_id,
                ExtractedRecord.field_template_id == extraction_request.field_template_id
            )
        )
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            logger.info("extraction_already_exists", 
                       document_id=str(document_id),
                       record_id=str(existing.id))
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document already extracted. Use force_reprocess=true to re-extract."
            )
    
    # Queue extraction task
    try:
        task = extract_document_task.delay(
            str(document_id),
            str(extraction_request.field_template_id)
        )
        
        logger.info("extraction_task_queued", 
                   document_id=str(document_id),
                   task_id=task.id)
        
        return TaskStatusResponse(
            task_id=task.id,
            task_type="extraction",
            status="PENDING",
            progress=0.0
        )
    
    except Exception as e:
        logger.error("extraction_queue_failed", 
                    document_id=str(document_id),
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue extraction task"
        )


@router.post("/projects/{project_id}/extract-all",
             response_model=TaskStatusResponse,
             status_code=status.HTTP_202_ACCEPTED)
async def trigger_project_extraction(
    project_id: UUID,
    force_reprocess: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger extraction for all documents in a project
    
    - **project_id**: UUID of the project
    - **force_reprocess**: Re-extract even if already extracted
    """
    logger.info("project_extraction_requested", project_id=str(project_id))
    
    # Get project with field template
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    if not project.field_template_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project does not have a field template assigned"
        )
    
    # Get all parsed documents
    docs_result = await db.execute(
        select(Document).where(
            Document.project_id == project_id,
            Document.upload_status == UploadStatus.PARSED
        )
    )
    documents = docs_result.scalars().all()
    
    if not documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No parsed documents found in project"
        )
    
    # Queue extraction tasks
    queued_count = 0
    for document in documents:
        # Check if already extracted (if not forcing)
        if not force_reprocess:
            existing_result = await db.execute(
                select(ExtractedRecord).where(
                    ExtractedRecord.document_id == document.id,
                    ExtractedRecord.field_template_id == project.field_template_id
                )
            )
            if existing_result.scalar_one_or_none():
                continue  # Skip already extracted
        
        try:
            extract_document_task.delay(
                str(document.id),
                str(project.field_template_id)
            )
            queued_count += 1
        except Exception as e:
            logger.error("extraction_queue_failed",
                        document_id=str(document.id),
                        error=str(e))
            continue
    
    logger.info("project_extraction_queued",
               project_id=str(project_id),
               queued_count=queued_count)
    
    return TaskStatusResponse(
        task_id=f"project-{project_id}",  # Pseudo task ID
        task_type="project_extraction",
        status="PENDING",
        progress=0.0,
        result={"documents_queued": queued_count}
    )


@router.get("/documents/{document_id}/extractions",
            response_model=List[ExtractedRecordResponse])
async def get_document_extractions(
    document_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all extraction records for a document
    
    - **document_id**: UUID of the document
    """
    # Verify document exists
    doc_result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    if not doc_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Get extraction records
    result = await db.execute(
        select(ExtractedRecord)
        .where(ExtractedRecord.document_id == document_id)
        .order_by(ExtractedRecord.created_at.desc())
    )
    
    records = result.scalars().all()
    return records


@router.get("/extractions/{record_id}",
            response_model=ExtractedRecordResponse)
async def get_extraction_record(
    record_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific extraction record
    
    - **record_id**: UUID of the extraction record
    """
    result = await db.execute(
        select(ExtractedRecord).where(ExtractedRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extraction record with ID {record_id} not found"
        )
    
    return record

