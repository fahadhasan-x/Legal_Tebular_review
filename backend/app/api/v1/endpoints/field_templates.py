"""
Field Template Endpoints
Manages extraction schema templates
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.config import settings
from app.db.session import get_db
from app.models import FieldTemplate
from app.schemas import FieldTemplateCreate, FieldTemplateUpdate, FieldTemplateResponse
from app.workers.tasks import re_extract_project_task

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/", 
             response_model=FieldTemplateResponse,
             status_code=status.HTTP_201_CREATED)
async def create_field_template(
    template_data: FieldTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new field template
    
    - **name**: Template name
    - **fields**: List of field definitions
    
    Returns:
        Created field template
    """
    logger.info("creating_field_template", name=template_data.name)
    
    # Validate field IDs are unique
    field_ids = [f.field_id for f in template_data.fields]
    if len(field_ids) != len(set(field_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field IDs must be unique within template"
        )
    
    # Convert Pydantic models to dicts for JSON storage
    fields_json = [f.model_dump() for f in template_data.fields]
    
    template = FieldTemplate(
        name=template_data.name,
        version=1,
        fields=fields_json
    )
    
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    logger.info("field_template_created", template_id=str(template.id))
    
    return template


@router.get("/", response_model=List[FieldTemplateResponse])
async def list_field_templates(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    List all field templates
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    result = await db.execute(
        select(FieldTemplate)
        .order_by(FieldTemplate.created_at.desc())
        .offset(skip)
        .limit(min(limit, settings.MAX_PAGE_SIZE))
    )
    
    templates = result.scalars().all()
    return templates


@router.get("/{template_id}", response_model=FieldTemplateResponse)
async def get_field_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific field template
    
    - **template_id**: UUID of the field template
    """
    result = await db.execute(
        select(FieldTemplate).where(FieldTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field template with ID {template_id} not found"
        )
    
    return template


@router.put("/{template_id}", response_model=FieldTemplateResponse)
async def update_field_template(
    template_id: UUID,
    template_data: FieldTemplateUpdate,
    trigger_re_extraction: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a field template
    
    - **template_id**: UUID of the field template
    - **trigger_re_extraction**: If true, re-extract all projects using this template
    
    IMPORTANT: Updating a template creates a new version. Projects using the old
    version will continue to use it unless explicitly updated.
    """
    result = await db.execute(
        select(FieldTemplate).where(FieldTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field template with ID {template_id} not found"
        )
    
    # Track if fields changed
    fields_changed = False
    
    if template_data.name is not None:
        template.name = template_data.name
    
    if template_data.fields is not None:
        # Validate field IDs are unique
        field_ids = [f.field_id for f in template_data.fields]
        if len(field_ids) != len(set(field_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Field IDs must be unique within template"
            )
        
        # Convert to JSON
        fields_json = [f.model_dump() for f in template_data.fields]
        
        # Check if fields actually changed
        if fields_json != template.fields:
            template.fields = fields_json
            template.version += 1
            fields_changed = True
            logger.info("template_fields_updated", 
                       template_id=str(template_id),
                       new_version=template.version)
    
    await db.commit()
    await db.refresh(template)
    
    logger.info("field_template_updated", template_id=str(template_id))
    
    # Trigger re-extraction if requested and fields changed
    if trigger_re_extraction and fields_changed:
        # Get all projects using this template
        from app.models import Project, ProjectStatus
        
        projects_result = await db.execute(
            select(Project).where(
                Project.field_template_id == template_id,
                Project.status == ProjectStatus.ACTIVE
            )
        )
        projects = projects_result.scalars().all()
        
        logger.info("triggering_re_extraction", 
                   template_id=str(template_id),
                   project_count=len(projects))
        
        for project in projects:
            try:
                re_extract_project_task.delay(str(project.id))
            except Exception as e:
                logger.error("re_extraction_queue_failed", 
                           project_id=str(project.id),
                           error=str(e))
    
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_field_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a field template
    
    - **template_id**: UUID of the field template
    
    NOTE: Cannot delete template if it's being used by any projects
    """
    result = await db.execute(
        select(FieldTemplate).where(FieldTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field template with ID {template_id} not found"
        )
    
    # Check if template is being used
    from app.models import Project
    
    usage_result = await db.execute(
        select(Project).where(Project.field_template_id == template_id).limit(1)
    )
    
    if usage_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete template that is being used by projects"
        )
    
    await db.delete(template)
    await db.commit()
    
    logger.info("field_template_deleted", template_id=str(template_id))
    return None

