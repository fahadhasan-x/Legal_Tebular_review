"""
Project Endpoints
CRUD operations for projects
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import structlog

from app.db.session import get_db
from app.models import Project, Document, ExtractedRecord, ExtractionStatus
from app.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetail,
)

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new project
    
    - **name**: Project name (required)
    - **description**: Project description (optional)
    - **field_template_id**: Field template ID (optional)
    """
    logger.info("creating_project", name=project_in.name)
    
    project = Project(
        name=project_in.name,
        description=project_in.description,
        field_template_id=project_in.field_template_id
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    logger.info("project_created", project_id=str(project.id))
    
    return project


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    List all projects with pagination
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Max number of records to return (default: 50, max: 100)
    """
    logger.info("listing_projects", skip=skip, limit=limit)
    
    # Limit max page size
    limit = min(limit, 100)
    
    result = await db.execute(
        select(Project)
        .order_by(Project.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    projects = result.scalars().all()
    
    return projects


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get project by ID with detailed statistics
    """
    logger.info("getting_project", project_id=str(project_id))
    
    # Get project with relationships
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.documents))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    # Calculate statistics
    doc_count = len(project.documents)
    
    # Count extracted documents
    extracted_result = await db.execute(
        select(func.count(ExtractedRecord.id.distinct()))
        .join(Document)
        .where(
            Document.project_id == project_id,
            ExtractedRecord.extraction_status == ExtractionStatus.COMPLETED
        )
    )
    extracted_count = extracted_result.scalar() or 0
    
    # Count pending documents
    pending_result = await db.execute(
        select(func.count(Document.id.distinct()))
        .outerjoin(ExtractedRecord)
        .where(
            Document.project_id == project_id,
            (ExtractedRecord.id.is_(None)) | 
            (ExtractedRecord.extraction_status.in_([
                ExtractionStatus.PENDING,
                ExtractionStatus.IN_PROGRESS
            ]))
        )
    )
    pending_count = pending_result.scalar() or 0
    
    # Build response
    return ProjectDetail(
        id=project.id,
        name=project.name,
        description=project.description,
        field_template_id=project.field_template_id,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        document_count=doc_count,
        extracted_count=extracted_count,
        pending_count=pending_count
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update project
    
    Note: Changing field_template_id will trigger re-extraction (handled by background task)
    """
    logger.info("updating_project", project_id=str(project_id))
    
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    # Track if template changed (for re-extraction trigger)
    template_changed = False
    if project_update.field_template_id and project_update.field_template_id != project.field_template_id:
        template_changed = True
    
    # Update fields
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    # TODO: Trigger re-extraction task if template changed
    if template_changed:
        logger.info("template_changed_reextraction_needed", project_id=str(project_id))
        # from app.workers.tasks import re_extract_project_task
        # re_extract_project_task.delay(str(project_id))
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete project (soft delete - sets status to ARCHIVED)
    """
    logger.info("deleting_project", project_id=str(project_id))
    
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    # Soft delete
    project.status = "ARCHIVED"
    await db.commit()
    
    logger.info("project_deleted", project_id=str(project_id))
    
    return None
