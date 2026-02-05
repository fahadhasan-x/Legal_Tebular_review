"""
Celery Tasks
Background tasks for document processing and extraction
"""
from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import structlog
from uuid import UUID

from app.core.config import settings
from app.models import Document, UploadStatus, ExtractedRecord, ExtractionStatus
from app.services.document_parser import DocumentParser, DocumentParserError

logger = structlog.get_logger(__name__)

# Create synchronous database engine for Celery workers
sync_engine = create_engine(settings.DATABASE_URL_SYNC, pool_pre_ping=True)


def get_sync_db():
    """Get synchronous database session for Celery tasks"""
    db = Session(sync_engine)
    try:
        return db
    except Exception as e:
        db.close()
        raise


@shared_task(bind=True, name="parse_document_task", max_retries=3, default_retry_delay=60)
def parse_document_task(self, document_id: str):
    """
    Parse uploaded document and extract text content
    
    Args:
        document_id: UUID of document to parse
        
    Process:
        1. Update status to PARSING
        2. Parse document using DocumentParser
        3. Save parsed text and metadata
        4. Update status to PARSED or FAILED
    """
    logger.info("parsing_document_task_started", document_id=document_id, task_id=self.request.id)
    
    db = get_sync_db()
    
    try:
        # Get document from database
        document = db.query(Document).filter(Document.id == UUID(document_id)).first()
        
        if not document:
            logger.error("document_not_found", document_id=document_id)
            return {"status": "error", "message": "Document not found"}
        
        # Update status to PARSING
        document.upload_status = UploadStatus.PARSING
        db.commit()
        
        logger.info("parsing_started", document_id=document_id, file_path=document.file_path)
        
        # Parse document
        parser = DocumentParser()
        result = parser.parse(document.file_path)
        
        # Update document with parsed data
        document.parsed_text = result['text']
        
        # Merge metadata
        existing_metadata = document.file_metadata or {}
        existing_metadata.update(result['metadata'])
        document.file_metadata = existing_metadata
        
        document.upload_status = UploadStatus.PARSED
        document.error_message = None
        
        db.commit()
        
        logger.info("parsing_document_task_completed", 
                   document_id=document_id,
                   text_length=len(result['text']),
                   word_count=result['metadata'].get('word_count', 0))
        
        # Auto-trigger extraction if project has field template
        if document.project and document.project.field_template_id:
            logger.info("auto_triggering_extraction", 
                       document_id=document_id,
                       template_id=str(document.project.field_template_id))
            
            extract_document_task.delay(
                document_id,
                str(document.project.field_template_id)
            )
        
        return {
            "status": "success",
            "document_id": document_id,
            "text_length": len(result['text']),
            "metadata": result['metadata']
        }
    
    except DocumentParserError as e:
        logger.error("parsing_failed", document_id=document_id, error=str(e))
        
        # Update document status
        document = db.query(Document).filter(Document.id == UUID(document_id)).first()
        if document:
            document.upload_status = UploadStatus.FAILED
            document.error_message = f"Parsing failed: {str(e)}"
            db.commit()
        
        return {"status": "error", "message": str(e)}
    
    except Exception as e:
        logger.error("parsing_document_task_failed", document_id=document_id, error=str(e), exc_info=True)
        
        # Update document status
        try:
            document = db.query(Document).filter(Document.id == UUID(document_id)).first()
            if document:
                document.upload_status = UploadStatus.FAILED
                document.error_message = f"Unexpected error: {str(e)}"
                db.commit()
        except:
            pass
        
        # Retry task
        raise self.retry(exc=e)
    
    finally:
        db.close()


@shared_task(bind=True, name="extract_document_task", max_retries=3, default_retry_delay=120)
def extract_document_task(self, document_id: str, field_template_id: str):
    """
    Extract fields from parsed document using Gemini LLM
    
    Args:
        document_id: UUID of document
        field_template_id: UUID of field template
        
    Process:
        1. Get document and field template
        2. Create or update ExtractedRecord with IN_PROGRESS status
        3. Use GeminiExtractor to extract fields
        4. Save extracted fields
        5. Update status to COMPLETED or FAILED
    """
    logger.info("extraction_task_started", 
               document_id=document_id, 
               template_id=field_template_id, 
               task_id=self.request.id)
    
    db = get_sync_db()
    
    try:
        from app.models import FieldTemplate
        from app.services.extractor import GeminiExtractor, ExtractionError
        
        # Get document
        document = db.query(Document).filter(Document.id == UUID(document_id)).first()
        if not document:
            logger.error("document_not_found", document_id=document_id)
            return {"status": "error", "message": "Document not found"}
        
        # Check if document is parsed
        if document.upload_status != UploadStatus.PARSED:
            logger.warning("document_not_parsed", 
                         document_id=document_id,
                         status=document.upload_status.value)
            return {"status": "error", "message": "Document not yet parsed"}
        
        if not document.parsed_text:
            logger.error("no_parsed_text", document_id=document_id)
            return {"status": "error", "message": "No parsed text available"}
        
        # Get field template
        template = db.query(FieldTemplate).filter(
            FieldTemplate.id == UUID(field_template_id)
        ).first()
        
        if not template:
            logger.error("template_not_found", template_id=field_template_id)
            return {"status": "error", "message": "Field template not found"}
        
        # Get or create ExtractedRecord
        extracted_record = db.query(ExtractedRecord).filter(
            ExtractedRecord.document_id == UUID(document_id),
            ExtractedRecord.field_template_id == UUID(field_template_id)
        ).first()
        
        if not extracted_record:
            extracted_record = ExtractedRecord(
                document_id=UUID(document_id),
                field_template_id=UUID(field_template_id),
                extraction_status=ExtractionStatus.IN_PROGRESS
            )
            db.add(extracted_record)
        else:
            extracted_record.extraction_status = ExtractionStatus.IN_PROGRESS
            extracted_record.error_message = None
        
        db.commit()
        
        logger.info("extraction_started", 
                   document_id=document_id,
                   text_length=len(document.parsed_text),
                   field_count=len(template.fields))
        
        # Extract fields using Gemini
        extractor = GeminiExtractor()
        extracted_fields = extractor.extract(
            document_text=document.parsed_text,
            field_definitions=template.fields
        )
        
        # Update extracted record
        extracted_record.extracted_fields = extracted_fields
        extracted_record.extraction_status = ExtractionStatus.COMPLETED
        extracted_record.error_message = None
        
        db.commit()
        
        # Calculate statistics
        fields_with_values = sum(1 for f in extracted_fields if f.get('raw_value'))
        avg_confidence = sum(f.get('confidence_score', 0) for f in extracted_fields) / len(extracted_fields) if extracted_fields else 0
        
        logger.info("extraction_task_completed", 
                   document_id=document_id,
                   fields_extracted=fields_with_values,
                   total_fields=len(extracted_fields),
                   avg_confidence=avg_confidence)
        
        return {
            "status": "success",
            "document_id": document_id,
            "extracted_record_id": str(extracted_record.id),
            "fields_extracted": fields_with_values,
            "avg_confidence": avg_confidence
        }
    
    except ExtractionError as e:
        logger.error("extraction_failed", document_id=document_id, error=str(e))
        
        # Update record status
        if extracted_record:
            extracted_record.extraction_status = ExtractionStatus.FAILED
            extracted_record.error_message = f"Extraction failed: {str(e)}"
            db.commit()
        
        return {"status": "error", "message": str(e)}
    
    except Exception as e:
        logger.error("extraction_task_failed", 
                    document_id=document_id, 
                    error=str(e), 
                    exc_info=True)
        
        # Update record status
        try:
            if extracted_record:
                extracted_record.extraction_status = ExtractionStatus.FAILED
                extracted_record.error_message = f"Unexpected error: {str(e)}"
                db.commit()
        except:
            pass
        
        # Retry task
        raise self.retry(exc=e)
    
    finally:
        db.close()


@shared_task(bind=True, name="re_extract_project_task")
def re_extract_project_task(self, project_id: str):
    """
    Re-extract all documents in a project
    Triggered when field template is updated
    
    Args:
        project_id: UUID of project
        
    Process:
        1. Get all parsed documents in project
        2. Queue extraction task for each document
    """
    logger.info("re_extraction_task_started", project_id=project_id, task_id=self.request.id)
    
    db = get_sync_db()
    
    try:
        from app.models import Project
        
        # Get project
        project = db.query(Project).filter(Project.id == UUID(project_id)).first()
        
        if not project:
            logger.error("project_not_found", project_id=project_id)
            return {"status": "error", "message": "Project not found"}
        
        if not project.field_template_id:
            logger.warning("no_template", project_id=project_id)
            return {"status": "error", "message": "Project has no field template"}
        
        # Get all parsed documents
        documents = db.query(Document).filter(
            Document.project_id == UUID(project_id),
            Document.upload_status == UploadStatus.PARSED
        ).all()
        
        logger.info("queuing_extractions", 
                   project_id=project_id,
                   document_count=len(documents))
        
        # Queue extraction tasks
        queued_count = 0
        for document in documents:
            try:
                extract_document_task.delay(
                    str(document.id),
                    str(project.field_template_id)
                )
                queued_count += 1
            except Exception as e:
                logger.error("task_queue_failed", 
                           document_id=str(document.id),
                           error=str(e))
                continue
        
        logger.info("re_extraction_task_completed", 
                   project_id=project_id,
                   queued_count=queued_count)
        
        return {
            "status": "success",
            "project_id": project_id,
            "documents_queued": queued_count
        }
    
    except Exception as e:
        logger.error("re_extraction_task_failed", 
                    project_id=project_id, 
                    error=str(e), 
                    exc_info=True)
        raise
    
    finally:
        db.close()

