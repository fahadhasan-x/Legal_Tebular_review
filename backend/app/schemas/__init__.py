"""
Pydantic Schemas
Request/Response models for API validation
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator

from app.models import ProjectStatus, UploadStatus, ExtractionStatus, ReviewStatus, FieldType


# ============================================================================
# Project Schemas
# ============================================================================

class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    field_template_id: Optional[UUID] = Field(None, description="Field template ID")


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    field_template_id: Optional[UUID] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: UUID
    name: str
    description: Optional[str]
    field_template_id: Optional[UUID]
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectDetail(ProjectResponse):
    """Schema for detailed project response with stats"""
    document_count: int = 0
    extracted_count: int = 0
    pending_count: int = 0


# ============================================================================
# Field Template Schemas
# ============================================================================

class FieldDefinition(BaseModel):
    """Schema for individual field definition"""
    field_id: str = Field(..., description="Unique field identifier")
    field_name: str = Field(..., description="Human-readable field name")
    field_type: FieldType = Field(..., description="Field data type")
    required: bool = Field(default=False, description="Is field required")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Validation rules")
    normalization: Optional[str] = Field(None, description="Normalization strategy")
    extraction_prompt: Optional[str] = Field(None, description="Custom extraction hint")


class FieldTemplateCreate(BaseModel):
    """Schema for creating field template"""
    name: str = Field(..., min_length=1, max_length=255)
    fields: List[FieldDefinition] = Field(..., min_items=1, description="Field definitions")


class FieldTemplateUpdate(BaseModel):
    """Schema for updating field template"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    fields: Optional[List[FieldDefinition]] = None


class FieldTemplateResponse(BaseModel):
    """Schema for field template response"""
    id: UUID
    name: str
    version: int
    fields: List[FieldDefinition]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Document Schemas
# ============================================================================

class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: UUID
    project_id: UUID
    filename: str
    file_type: str
    file_size: int
    upload_status: UploadStatus
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentDetail(DocumentResponse):
    """Schema for detailed document response"""
    parsed_text_preview: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    extraction_status: Optional[ExtractionStatus] = None


# ============================================================================
# Extraction Schemas
# ============================================================================

class Citation(BaseModel):
    """Schema for source citation"""
    source: str = Field(..., description="Citation source (e.g., 'page 1, section 2')")
    text_snippet: str = Field(..., description="Text snippet from document")


class ExtractedField(BaseModel):
    """Schema for single extracted field"""
    field_id: str
    raw_value: Optional[str] = None
    normalized_value: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence 0-1")
    citations: List[Citation] = Field(default_factory=list)


class ExtractionRequest(BaseModel):
    """Schema for extraction request"""
    field_template_id: UUID
    force_reprocess: bool = False


class ExtractedRecordResponse(BaseModel):
    """Schema for extracted record response"""
    id: UUID
    document_id: UUID
    field_template_id: UUID
    extraction_status: ExtractionStatus
    extracted_fields: Optional[List[ExtractedField]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Review Schemas
# ============================================================================

class ReviewRecordCreate(BaseModel):
    """Schema for creating review record"""
    extracted_record_id: UUID
    field_id: str
    review_status: ReviewStatus
    manual_value: Optional[str] = None
    reviewer_notes: Optional[str] = None


class ReviewRecordResponse(BaseModel):
    """Schema for review record response"""
    id: UUID
    extracted_record_id: UUID
    field_id: str
    review_status: ReviewStatus
    manual_value: Optional[str]
    reviewer_notes: Optional[str]
    reviewed_by: Optional[str]
    reviewed_at: datetime
    
    class Config:
        from_attributes = True


class ReviewTableRow(BaseModel):
    """Schema for review table row"""
    document_id: UUID
    document_name: str
    fields: Dict[str, Any]  # field_id -> field data with value, confidence, status


class ReviewTableResponse(BaseModel):
    """Schema for review table response"""
    columns: List[str]  # Field names for table headers
    rows: List[ReviewTableRow]


# ============================================================================
# Evaluation Schemas
# ============================================================================

class GroundTruthLabel(BaseModel):
    """Schema for human-labeled ground truth"""
    document_id: UUID
    field_id: str
    ground_truth: str


class EvaluationRequest(BaseModel):
    """Schema for evaluation request"""
    human_labels: List[GroundTruthLabel]


class EvaluationMetrics(BaseModel):
    """Schema for evaluation metrics"""
    field_accuracy: float
    exact_match: float
    coverage: float
    per_field_scores: Dict[str, float]


class EvaluationResultResponse(BaseModel):
    """Schema for evaluation result response"""
    id: UUID
    project_id: UUID
    evaluation_type: str
    metrics: EvaluationMetrics
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Task Status Schemas
# ============================================================================

class TaskStatusResponse(BaseModel):
    """Schema for async task status"""
    task_id: str
    task_type: str
    status: str  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    progress: float = Field(..., ge=0.0, le=1.0)
    result: Optional[Any] = None
    error: Optional[str] = None


# ============================================================================
# Generic Response Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
    error: Optional[str] = None


class SuccessResponse(BaseModel):
    """Schema for generic success responses"""
    message: str
    data: Optional[Any] = None
