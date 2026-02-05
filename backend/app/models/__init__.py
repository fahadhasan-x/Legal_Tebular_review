"""
Database Models
SQLAlchemy ORM models for all entities
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, Enum, JSON, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


# Enums
class ProjectStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class UploadStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PARSING = "PARSING"
    PARSED = "PARSED"
    FAILED = "FAILED"


class ExtractionStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ReviewStatus(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    MANUAL_UPDATED = "MANUAL_UPDATED"
    MISSING_DATA = "MISSING_DATA"
    PENDING = "PENDING"


class FieldType(str, enum.Enum):
    TEXT = "TEXT"
    DATE = "DATE"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    LIST = "LIST"


# Models
class Project(Base):
    """
    Project model - Container for documents and field templates
    """
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    field_template_id = Column(UUID(as_uuid=True), ForeignKey("field_templates.id"), nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    field_template = relationship("FieldTemplate", back_populates="projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    evaluation_results = relationship("EvaluationResult", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project {self.name}>"


class FieldTemplate(Base):
    """
    Field Template model - Defines extraction schema
    """
    __tablename__ = "field_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    fields = Column(JSON, nullable=False)  # Array of field definitions
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    projects = relationship("Project", back_populates="field_template")
    extracted_records = relationship("ExtractedRecord", back_populates="field_template")
    
    def __repr__(self):
        return f"<FieldTemplate {self.name} v{self.version}>"


class Document(Base):
    """
    Document model - Uploaded legal documents
    """
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_path = Column(Text, nullable=False)
    upload_status = Column(Enum(UploadStatus), default=UploadStatus.UPLOADED, nullable=False)
    parsed_text = Column(Text, nullable=True)
    file_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="documents")
    extracted_records = relationship("ExtractedRecord", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document {self.filename}>"


class ExtractedRecord(Base):
    """
    Extracted Record model - AI extraction results
    """
    __tablename__ = "extracted_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    field_template_id = Column(UUID(as_uuid=True), ForeignKey("field_templates.id"), nullable=False)
    extraction_status = Column(Enum(ExtractionStatus), default=ExtractionStatus.PENDING, nullable=False)
    extracted_fields = Column(JSON, nullable=True)  # Array of field results
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="extracted_records")
    field_template = relationship("FieldTemplate", back_populates="extracted_records")
    review_records = relationship("ReviewRecord", back_populates="extracted_record", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ExtractedRecord {self.id}>"


class ReviewRecord(Base):
    """
    Review Record model - Manual review and edits
    """
    __tablename__ = "review_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    extracted_record_id = Column(UUID(as_uuid=True), ForeignKey("extracted_records.id"), nullable=False, index=True)
    field_id = Column(String(100), nullable=False, index=True)
    review_status = Column(Enum(ReviewStatus), nullable=False)
    manual_value = Column(Text, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(100), nullable=True)  # User ID (future)
    reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    extracted_record = relationship("ExtractedRecord", back_populates="review_records")
    
    def __repr__(self):
        return f"<ReviewRecord {self.field_id}: {self.review_status}>"


class EvaluationResult(Base):
    """
    Evaluation Result model - Accuracy metrics
    """
    __tablename__ = "evaluation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    evaluation_type = Column(String(50), nullable=False)
    metrics = Column(JSON, nullable=False)  # Accuracy, coverage, per-field scores
    human_labels_path = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="evaluation_results")
    
    def __repr__(self):
        return f"<EvaluationResult {self.evaluation_type}>"
