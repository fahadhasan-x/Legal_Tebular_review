"""
Review Endpoints
Human review and manual editing of extracted data
"""
from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import structlog

from app.db.session import get_db
from app.models import (
    ReviewRecord, ExtractedRecord, Document, Project,
    ReviewStatus, ExtractionStatus
)
from app.schemas import (
    ReviewRecordCreate,
    ReviewRecordResponse,
    ReviewTableResponse,
    ReviewTableRow
)

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/reviews",
             response_model=ReviewRecordResponse,
             status_code=status.HTTP_201_CREATED)
async def create_review_record(
    review_data: ReviewRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create or update a review record for an extracted field
    
    - **extracted_record_id**: UUID of the extracted record
    - **field_id**: Field identifier
    - **review_status**: Review status (CONFIRMED, REJECTED, etc.)
    - **manual_value**: Manual correction (optional)
    - **reviewer_notes**: Additional notes (optional)
    """
    logger.info("creating_review_record",
               extracted_record_id=str(review_data.extracted_record_id),
               field_id=review_data.field_id)
    
    # Verify extracted record exists
    extracted_result = await db.execute(
        select(ExtractedRecord).where(
            ExtractedRecord.id == review_data.extracted_record_id
        )
    )
    extracted_record = extracted_result.scalar_one_or_none()
    
    if not extracted_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extracted record with ID {review_data.extracted_record_id} not found"
        )
    
    # Verify field exists in extracted data
    if extracted_record.extracted_fields:
        field_exists = any(
            f.get('field_id') == review_data.field_id 
            for f in extracted_record.extracted_fields
        )
        if not field_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{review_data.field_id}' not found in extracted record"
            )
    
    # Check if review already exists
    existing_result = await db.execute(
        select(ReviewRecord).where(
            and_(
                ReviewRecord.extracted_record_id == review_data.extracted_record_id,
                ReviewRecord.field_id == review_data.field_id
            )
        )
    )
    existing_review = existing_result.scalar_one_or_none()
    
    if existing_review:
        # Update existing review
        existing_review.review_status = review_data.review_status
        existing_review.manual_value = review_data.manual_value
        existing_review.reviewer_notes = review_data.reviewer_notes
        # reviewed_at will auto-update via onupdate
        
        await db.commit()
        await db.refresh(existing_review)
        
        logger.info("review_record_updated", review_id=str(existing_review.id))
        return existing_review
    
    else:
        # Create new review
        review = ReviewRecord(
            extracted_record_id=review_data.extracted_record_id,
            field_id=review_data.field_id,
            review_status=review_data.review_status,
            manual_value=review_data.manual_value,
            reviewer_notes=review_data.reviewer_notes,
            reviewed_by=None  # TODO: Add authentication and set user ID
        )
        
        db.add(review)
        await db.commit()
        await db.refresh(review)
        
        logger.info("review_record_created", review_id=str(review.id))
        return review


@router.get("/extractions/{extracted_record_id}/reviews",
            response_model=List[ReviewRecordResponse])
async def get_extraction_reviews(
    extracted_record_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all review records for an extracted record
    
    - **extracted_record_id**: UUID of the extracted record
    """
    # Verify extracted record exists
    extracted_result = await db.execute(
        select(ExtractedRecord).where(ExtractedRecord.id == extracted_record_id)
    )
    if not extracted_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extracted record with ID {extracted_record_id} not found"
        )
    
    # Get reviews
    result = await db.execute(
        select(ReviewRecord)
        .where(ReviewRecord.extracted_record_id == extracted_record_id)
        .order_by(ReviewRecord.reviewed_at.desc())
    )
    
    reviews = result.scalars().all()
    return reviews


@router.get("/projects/{project_id}/review-table",
            response_model=ReviewTableResponse)
async def get_project_review_table(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get review table data for a project
    
    Returns a structured table with:
    - Columns: Field names from template
    - Rows: Each document with extracted values, confidence, and review status
    
    This is the main endpoint for the review UI.
    """
    logger.info("fetching_review_table", project_id=str(project_id))
    
    # Get project with field template
    project_result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    if not project.field_template_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project does not have a field template"
        )
    
    # Get field template
    template = project.field_template
    if not template:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Field template not found"
        )
    
    # Extract column names
    columns = [field['field_name'] for field in template.fields]
    
    # Get all documents with their extractions
    docs_result = await db.execute(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.created_at.asc())
    )
    documents = docs_result.scalars().all()
    
    rows = []
    
    for document in documents:
        # Get latest extraction for this document
        extraction_result = await db.execute(
            select(ExtractedRecord)
            .where(
                and_(
                    ExtractedRecord.document_id == document.id,
                    ExtractedRecord.field_template_id == project.field_template_id
                )
            )
            .order_by(ExtractedRecord.created_at.desc())
            .limit(1)
        )
        extraction = extraction_result.scalar_one_or_none()
        
        # Build field data
        field_data = {}
        
        if extraction and extraction.extraction_status == ExtractionStatus.COMPLETED:
            # Get review records for this extraction
            reviews_result = await db.execute(
                select(ReviewRecord)
                .where(ReviewRecord.extracted_record_id == extraction.id)
            )
            reviews = {r.field_id: r for r in reviews_result.scalars().all()}
            
            # Process each field
            for field_def in template.fields:
                field_id = field_def['field_id']
                
                # Find extracted value
                extracted_field = next(
                    (f for f in extraction.extracted_fields if f['field_id'] == field_id),
                    None
                )
                
                # Get review if exists
                review = reviews.get(field_id)
                
                # Build field data
                if extracted_field:
                    field_data[field_id] = {
                        "field_name": field_def['field_name'],
                        "extracted_value": extracted_field.get('raw_value'),
                        "normalized_value": extracted_field.get('normalized_value'),
                        "confidence_score": extracted_field.get('confidence_score', 0.0),
                        "review_status": review.review_status.value if review else ReviewStatus.PENDING.value,
                        "manual_value": review.manual_value if review else None,
                        "final_value": review.manual_value if review and review.manual_value else extracted_field.get('normalized_value'),
                        "citations": extracted_field.get('citations', [])
                    }
                else:
                    # Field not found in extraction
                    field_data[field_id] = {
                        "field_name": field_def['field_name'],
                        "extracted_value": None,
                        "normalized_value": None,
                        "confidence_score": 0.0,
                        "review_status": ReviewStatus.MISSING_DATA.value,
                        "manual_value": review.manual_value if review else None,
                        "final_value": review.manual_value if review else None,
                        "citations": []
                    }
        else:
            # No extraction or failed extraction
            for field_def in template.fields:
                field_data[field_def['field_id']] = {
                    "field_name": field_def['field_name'],
                    "extracted_value": None,
                    "normalized_value": None,
                    "confidence_score": 0.0,
                    "review_status": "NOT_EXTRACTED",
                    "manual_value": None,
                    "final_value": None,
                    "citations": []
                }
        
        rows.append(ReviewTableRow(
            document_id=document.id,
            document_name=document.filename,
            fields=field_data
        ))
    
    logger.info("review_table_fetched",
               project_id=str(project_id),
               document_count=len(rows),
               field_count=len(columns))
    
    return ReviewTableResponse(
        columns=columns,
        rows=rows
    )


@router.post("/reviews/bulk",
             response_model=Dict[str, Any],
             status_code=status.HTTP_201_CREATED)
async def bulk_create_reviews(
    reviews_data: List[ReviewRecordCreate],
    db: AsyncSession = Depends(get_db)
):
    """
    Create or update multiple review records at once
    
    Useful for batch operations in the review UI.
    """
    logger.info("bulk_review_creation", count=len(reviews_data))
    
    created_count = 0
    updated_count = 0
    errors = []
    
    for review_data in reviews_data:
        try:
            # Check if exists
            existing_result = await db.execute(
                select(ReviewRecord).where(
                    and_(
                        ReviewRecord.extracted_record_id == review_data.extracted_record_id,
                        ReviewRecord.field_id == review_data.field_id
                    )
                )
            )
            existing = existing_result.scalar_one_or_none()
            
            if existing:
                # Update
                existing.review_status = review_data.review_status
                existing.manual_value = review_data.manual_value
                existing.reviewer_notes = review_data.reviewer_notes
                updated_count += 1
            else:
                # Create
                review = ReviewRecord(
                    extracted_record_id=review_data.extracted_record_id,
                    field_id=review_data.field_id,
                    review_status=review_data.review_status,
                    manual_value=review_data.manual_value,
                    reviewer_notes=review_data.reviewer_notes
                )
                db.add(review)
                created_count += 1
        
        except Exception as e:
            logger.error("bulk_review_error",
                        extracted_record_id=str(review_data.extracted_record_id),
                        field_id=review_data.field_id,
                        error=str(e))
            errors.append({
                "extracted_record_id": str(review_data.extracted_record_id),
                "field_id": review_data.field_id,
                "error": str(e)
            })
            continue
    
    await db.commit()
    
    logger.info("bulk_review_completed",
               created=created_count,
               updated=updated_count,
               errors=len(errors))
    
    return {
        "created": created_count,
        "updated": updated_count,
        "total": len(reviews_data),
        "errors": errors
    }

