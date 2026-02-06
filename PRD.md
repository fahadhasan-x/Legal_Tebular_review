# Legal Tabular Review System - Product Requirements Document (PRD)

**Version:** 1.0  
**Last Updated:** February 2025  
**Status:** Planning Phase  
**Author:** Development Team

---

## 📋 Executive Summary

### Project Overview
Legal Tabular Review System is a full-stack AI-powered platform that ingests multiple legal documents (contracts, agreements, regulatory filings), extracts key information using LLMs, and presents structured data in a tabular format for side-by-side comparison and review workflows.

### Problem Statement
Legal teams waste significant time manually comparing multiple contracts to extract and align key terms (parties, dates, payment terms, liability clauses). Current solutions require manual reading, copy-pasting into spreadsheets, and inconsistent field extraction.

### Solution
An intelligent system that:
- Automatically parses legal documents (PDF, DOCX, HTML)
- Extracts customizable fields using AI (Gemini LLM)
- Generates structured comparison tables
- Enables review workflows with confidence scoring and citations
- Supports quality evaluation against human benchmarks

### Success Metrics
- **Extraction Accuracy:** >85% field-level accuracy vs human labels
- **Time Savings:** 70% reduction in document comparison time
- **Coverage:** Successfully extract 90%+ of defined fields
- **User Satisfaction:** Review workflow reduces manual edits by 60%

---

## 🎯 Goals and Non-Goals

### Goals
✅ Support multiple document formats (PDF, DOCX, HTML, TXT)  
✅ Customizable field templates (user-defined extraction schema)  
✅ High-quality extraction with citations and confidence scores  
✅ Review workflow (approve/reject/manual edit)  
✅ Side-by-side comparison table view  
✅ Quality evaluation (AI vs human comparison)  
✅ Async processing with status tracking  
✅ Export results (CSV/Excel)

### Non-Goals
❌ Automated legal opinions or decision-making  
❌ Multi-language support (English only for MVP)  
❌ Real-time collaborative editing  
❌ Complex cross-jurisdiction legal reasoning  
❌ E-signature or workflow automation beyond review

---

## 👥 Target Users

### Primary Users
1. **Legal Analysts** - Compare vendor contracts, identify risks
2. **Compliance Officers** - Review regulatory filings, ensure consistency
3. **In-house Counsel** - Quick contract review and clause comparison

### User Personas
**Sarah - Corporate Paralegal**
- Reviews 20+ NDAs/contracts monthly
- Needs to extract key terms quickly
- Pain point: Manual spreadsheet creation

**David - Compliance Manager**
- Audits supplier agreements for standard clauses
- Requires accuracy and audit trails
- Pain point: Inconsistent field extraction

---

## 🏗️ System Architecture

### High-Level Architecture
```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Next.js   │◄────►│   FastAPI    │◄────►│ PostgreSQL  │
│  Frontend   │      │   Backend    │      │  Database   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                     ┌──────┴──────┐
                     │             │
              ┌──────▼────┐  ┌────▼─────┐
              │  Gemini   │  │  Redis/  │
              │    API    │  │  Celery  │
              └───────────┘  └──────────┘
```

### Component Boundaries

#### Frontend (Next.js + TypeScript)
- **Pages:** Project list, detail, document upload, table review, evaluation
- **Components:** File uploader, table grid, review panel, status tracker
- **State:** React Query for server state, Zustand for client state
- **Styling:** Tailwind CSS + shadcn/ui

#### Backend (FastAPI + Python)
- **API Layer:** REST endpoints, request validation (Pydantic)
- **Services:** Project management, extraction, review, evaluation
- **Workers:** Celery for async tasks (ingestion, extraction, evaluation)
- **Storage:** PostgreSQL (metadata), S3/local (documents), Redis (cache/queue)

#### AI/ML Layer
- **Primary LLM:** Google Gemini 1.5 Flash (FREE tier)
- **Fallback:** Groq API (Llama 3.1)
- **Orchestration:** LangChain for prompt management and structured output
- **Document Parsing:** PyPDF2, python-docx, BeautifulSoup

---

## 📊 Data Model

### Core Entities

#### 1. Project
```python
{
  "id": "uuid",
  "name": "Q4 2024 Vendor Contracts",
  "description": "Review supplier agreements",
  "field_template_id": "uuid",
  "status": "ACTIVE | ARCHIVED",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

#### 2. FieldTemplate
```python
{
  "id": "uuid",
  "name": "Standard Contract Template",
  "version": 2,
  "fields": [
    {
      "field_id": "parties",
      "field_name": "Contracting Parties",
      "field_type": "TEXT | DATE | NUMBER | BOOLEAN | LIST",
      "required": true,
      "validation_rules": {"max_length": 500},
      "normalization": "UPPERCASE | LOWERCASE | DATE_ISO"
    }
  ],
  "created_at": "timestamp"
}
```

#### 3. Document
```python
{
  "id": "uuid",
  "project_id": "uuid",
  "filename": "contract_acme.pdf",
  "file_type": "PDF | DOCX | HTML | TXT",
  "file_size": 1024000,
  "file_path": "s3://bucket/project_id/doc_id.pdf",
  "upload_status": "UPLOADED | PARSING | PARSED | FAILED",
  "parsed_text": "full document text",
  "metadata": {"pages": 12, "author": "Legal Dept"},
  "created_at": "timestamp"
}
```

#### 4. ExtractedRecord
```python
{
  "id": "uuid",
  "document_id": "uuid",
  "field_template_id": "uuid",
  "extraction_status": "PENDING | IN_PROGRESS | COMPLETED | FAILED",
  "extracted_fields": [
    {
      "field_id": "parties",
      "raw_value": "Acme Corp and XYZ Ltd",
      "normalized_value": "ACME CORP, XYZ LTD",
      "confidence_score": 0.95,
      "citations": [
        {
          "source": "page 1, paragraph 2",
          "text_snippet": "This Agreement is between Acme Corp..."
        }
      ]
    }
  ],
  "created_at": "timestamp"
}
```

#### 5. ReviewRecord
```python
{
  "id": "uuid",
  "extracted_record_id": "uuid",
  "field_id": "parties",
  "review_status": "CONFIRMED | REJECTED | MANUAL_UPDATED | MISSING_DATA",
  "manual_value": "Acme Corporation, XYZ Limited",  # if edited
  "reviewer_notes": "Updated to full legal names",
  "reviewed_by": "user_id",
  "reviewed_at": "timestamp"
}
```

#### 6. EvaluationResult
```python
{
  "id": "uuid",
  "project_id": "uuid",
  "evaluation_type": "ACCURACY | COVERAGE | CONSISTENCY",
  "metrics": {
    "field_accuracy": 0.87,
    "exact_match": 0.72,
    "coverage": 0.93,
    "per_field_scores": {
      "parties": 0.95,
      "dates": 0.88
    }
  },
  "human_labels_path": "s3://bucket/eval_labels.json",
  "created_at": "timestamp"
}
```

### Database Schema (PostgreSQL)

```sql
-- Projects table
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  field_template_id UUID REFERENCES field_templates(id),
  status VARCHAR(50) DEFAULT 'ACTIVE',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Field Templates table
CREATE TABLE field_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  version INTEGER DEFAULT 1,
  fields JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Documents table
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  filename VARCHAR(500) NOT NULL,
  file_type VARCHAR(50),
  file_size BIGINT,
  file_path TEXT,
  upload_status VARCHAR(50) DEFAULT 'UPLOADED',
  parsed_text TEXT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Extracted Records table
CREATE TABLE extracted_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
  field_template_id UUID REFERENCES field_templates(id),
  extraction_status VARCHAR(50) DEFAULT 'PENDING',
  extracted_fields JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Review Records table
CREATE TABLE review_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  extracted_record_id UUID REFERENCES extracted_records(id) ON DELETE CASCADE,
  field_id VARCHAR(100),
  review_status VARCHAR(50) NOT NULL,
  manual_value TEXT,
  reviewer_notes TEXT,
  reviewed_by VARCHAR(100),
  reviewed_at TIMESTAMP DEFAULT NOW()
);

-- Evaluation Results table
CREATE TABLE evaluation_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  evaluation_type VARCHAR(50),
  metrics JSONB,
  human_labels_path TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_documents_project ON documents(project_id);
CREATE INDEX idx_extracted_records_document ON extracted_records(document_id);
CREATE INDEX idx_review_records_extracted ON review_records(extracted_record_id);
```

---

## 🔌 API Design

### Base URL
```
Production: https://api.legal-review.com/v1
Development: http://localhost:8000/api/v1
```

### Authentication
- JWT tokens (future)
- API keys for service accounts
- MVP: No auth (internal tool)

### Endpoints

#### 1. Project Management

**POST /projects**
```json
Request:
{
  "name": "Q4 Contracts Review",
  "description": "Vendor agreements review",
  "field_template_id": "uuid-or-null"
}

Response: 201 Created
{
  "id": "uuid",
  "name": "Q4 Contracts Review",
  "status": "ACTIVE",
  "created_at": "2025-02-03T10:00:00Z"
}
```

**GET /projects/{project_id}**
```json
Response: 200 OK
{
  "id": "uuid",
  "name": "Q4 Contracts Review",
  "description": "...",
  "field_template": { /* template object */ },
  "documents": [ /* array of documents */ ],
  "stats": {
    "total_documents": 15,
    "extracted": 12,
    "pending": 3
  }
}
```

**PUT /projects/{project_id}**
```json
Request:
{
  "name": "Updated Name",
  "field_template_id": "new-uuid"  # Triggers re-extraction
}

Response: 200 OK
{
  "id": "uuid",
  "re_extraction_triggered": true,
  "task_id": "celery-task-uuid"
}
```

#### 2. Field Template Management

**POST /field-templates**
```json
Request:
{
  "name": "Contract Template v2",
  "fields": [
    {
      "field_id": "parties",
      "field_name": "Contracting Parties",
      "field_type": "TEXT",
      "required": true,
      "extraction_prompt": "Extract all party names from the contract"
    }
  ]
}

Response: 201 Created
{
  "id": "uuid",
  "version": 1
}
```

#### 3. Document Ingestion

**POST /projects/{project_id}/documents/upload**
```json
Content-Type: multipart/form-data

Request:
- file: [binary]
- metadata: {"source": "email", "priority": "high"}

Response: 202 Accepted
{
  "document_id": "uuid",
  "task_id": "parse-task-uuid",
  "status": "PARSING"
}
```

**GET /documents/{document_id}/status**
```json
Response: 200 OK
{
  "id": "uuid",
  "filename": "contract.pdf",
  "upload_status": "PARSED",
  "parsed_text_preview": "This Agreement...",
  "extraction_status": "IN_PROGRESS"
}
```

#### 4. Extraction

**POST /documents/{document_id}/extract**
```json
Request:
{
  "field_template_id": "uuid",
  "force_reprocess": false
}

Response: 202 Accepted
{
  "extraction_task_id": "uuid",
  "estimated_time": "30s"
}
```

**GET /extracted-records/{record_id}**
```json
Response: 200 OK
{
  "id": "uuid",
  "document_id": "uuid",
  "extraction_status": "COMPLETED",
  "extracted_fields": [
    {
      "field_id": "effective_date",
      "raw_value": "January 15, 2024",
      "normalized_value": "2024-01-15",
      "confidence_score": 0.92,
      "citations": [
        {
          "source": "page 1, section 1.1",
          "text_snippet": "Effective Date: January 15, 2024"
        }
      ]
    }
  ]
}
```

#### 5. Review Workflow

**POST /review-records**
```json
Request:
{
  "extracted_record_id": "uuid",
  "field_id": "parties",
  "review_status": "MANUAL_UPDATED",
  "manual_value": "Corrected Party Name",
  "reviewer_notes": "Fixed abbreviation"
}

Response: 201 Created
{
  "id": "uuid",
  "review_status": "MANUAL_UPDATED"
}
```

**GET /projects/{project_id}/review-table**
```json
Response: 200 OK
{
  "columns": ["Document", "Parties", "Effective Date", "Term"],
  "rows": [
    {
      "document_id": "uuid-1",
      "document_name": "contract_a.pdf",
      "fields": {
        "parties": {
          "value": "Acme Corp, XYZ Ltd",
          "confidence": 0.95,
          "review_status": "CONFIRMED"
        },
        "effective_date": {
          "value": "2024-01-15",
          "confidence": 0.88,
          "review_status": "PENDING"
        }
      }
    }
  ]
}
```

#### 6. Evaluation

**POST /projects/{project_id}/evaluate**
```json
Request:
{
  "human_labels": [
    {
      "document_id": "uuid",
      "field_id": "parties",
      "ground_truth": "Acme Corporation, XYZ Limited"
    }
  ]
}

Response: 200 OK
{
  "evaluation_id": "uuid",
  "metrics": {
    "field_accuracy": 0.87,
    "coverage": 0.93
  }
}
```

#### 7. Status Tracking

**GET /tasks/{task_id}/status**
```json
Response: 200 OK
{
  "task_id": "uuid",
  "task_type": "EXTRACTION",
  "status": "IN_PROGRESS | COMPLETED | FAILED",
  "progress": 0.65,
  "result": { /* task output if completed */ },
  "error": "error message if failed"
}
```

---

## 🔄 Data Flow & Workflows

### Workflow 1: Document Upload → Extraction → Review

```
1. User uploads document (PDF)
   ↓
2. Backend: Parse document (PyPDF2)
   ↓
3. Store parsed text in database
   ↓
4. Trigger async extraction task (Celery)
   ↓
5. Extraction worker:
   - Load field template
   - Call Gemini API with prompt
   - Parse structured output
   - Extract citations and confidence
   ↓
6. Store ExtractedRecord in database
   ↓
7. Frontend: Display in review table
   ↓
8. User reviews: CONFIRM / REJECT / EDIT
   ↓
9. Store ReviewRecord with manual edits
```

### Workflow 2: Template Update → Re-extraction

```
1. User updates field template
   ↓
2. Backend: Create new template version
   ↓
3. Trigger re-extraction for all documents in projects using this template
   ↓
4. Celery tasks: Re-run extraction with new fields
   ↓
5. Compare with old results (audit trail)
   ↓
6. Frontend: Show updated table with change indicators
```

### Workflow 3: Quality Evaluation

```
1. User provides human-labeled ground truth
   ↓
2. Backend: Load AI extracted results
   ↓
3. Compare field-by-field:
   - Exact match
   - Semantic similarity (embeddings)
   - Normalized match
   ↓
4. Calculate metrics:
   - Accuracy = correct / total
   - Coverage = extracted / required
   - F1 score per field
   ↓
5. Generate evaluation report
   ↓
6. Frontend: Display metrics + per-document breakdown
```

---

## 🧠 AI/LLM Integration

### Extraction Strategy

#### LLM Selection
- **Primary:** Google Gemini 1.5 Flash
  - FREE tier: 1500 requests/day
  - Long context: 1M tokens (perfect for long contracts)
  - Structured output support
- **Fallback:** Groq API (Llama 3.1)
- **Future:** Ollama for fully local deployment

#### Smart Chunking for Large Documents
For documents >100 pages, implement intelligent chunking:
```python
def smart_chunk_document(doc_text: str, max_tokens: int = 30000):
    """Split document at section boundaries, not arbitrary tokens"""
    sections = extract_sections(doc_text)  # Use PDF bookmarks or heading detection
    chunks = []
    current_chunk = []
    current_size = 0
    
    for section in sections:
        section_size = count_tokens(section)
        if current_size + section_size > max_tokens:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [section]
            current_size = section_size
        else:
            current_chunk.append(section)
            current_size += section_size
    
    return chunks
```

#### Field-Specific Prompts
Different fields need different extraction strategies:

**For Dates:**
```python
date_prompt = """
Extract the {field_name} from this contract.
Look for phrases like: "Effective Date", "Commencement Date", "Start Date"
Format: YYYY-MM-DD
If multiple dates found, return the earliest one as the effective date.
Confidence: HIGH if explicitly labeled, MEDIUM if inferred from context.
"""
```

**For Monetary Amounts:**
```python
amount_prompt = """
Extract {field_name} (contract value, payment amount, etc.).
- Include currency symbol and amount
- Normalize to standard format: USD 1,000,000.00
- If range given (e.g., $1M-$2M), extract the maximum
- Confidence: HIGH if exact number, MEDIUM if "approximately"
"""
```

**For Legal Entities (Parties):**
```python
parties_prompt = """
Extract all contracting parties.
- Include full legal names (not abbreviations)
- Format: "Party A, Party B"
- Distinguish between primary parties and guarantors/witnesses
- Look in: first page, signature blocks, "BETWEEN" clauses
Confidence: HIGH if in standard "BETWEEN X AND Y" format
"""
```

#### Prompt Engineering

**System Prompt Template:**
```
You are an expert legal document analyst. Extract the following fields from the provided contract document. For each field, provide:
1. The extracted value (exact text from document)
2. Citation (page/section reference)
3. Confidence score (0.0-1.0)
4. Normalized output (formatted per rules)

Field Definitions:
{field_template_json}

Document Text:
{document_text}

Output Format (JSON):
{
  "fields": [
    {
      "field_id": "parties",
      "raw_value": "exact text",
      "normalized_value": "NORMALIZED TEXT",
      "confidence_score": 0.95,
      "citations": [{"source": "page 1, para 2", "snippet": "..."}]
    }
  ]
}

If a field is not found, set raw_value to null and confidence to 0.0.
```

#### Structured Output
Use Gemini's schema enforcement:
```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser

class ExtractedField(BaseModel):
    field_id: str
    raw_value: Optional[str]
    normalized_value: Optional[str]
    confidence_score: float = Field(ge=0.0, le=1.0)
    citations: List[Citation]

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.1
)
parser = PydanticOutputParser(pydantic_object=ExtractedField)
```

#### Confidence Scoring
**Automated Confidence Calculation:**
```python
def calculate_confidence(field_value: str, context: dict) -> float:
    """
    Multi-factor confidence scoring
    """
    base_confidence = 0.5
    
    # Factor 1: Explicit label match (+0.3)
    if has_explicit_label(context['text_snippet'], field_name):
        base_confidence += 0.3
    
    # Factor 2: Multiple occurrences consistency (+0.2)
    occurrences = find_all_occurrences(document, field_value)
    if len(occurrences) > 1 and all_consistent(occurrences):
        base_confidence += 0.2
    
    # Factor 3: Validation rules pass (+0.1)
    if passes_validation(field_value, field_type):
        base_confidence += 0.1
    
    # Factor 4: Position in document (+0.1)
    if is_in_expected_location(context['page'], field_type):
        base_confidence += 0.1
    
    # Penalty: Ambiguous wording (-0.2)
    if contains_ambiguous_terms(context['text_snippet']):
        base_confidence -= 0.2
    
    return min(max(base_confidence, 0.0), 1.0)
```

**Confidence Levels:**
- **High (>0.9):** Direct match with clear citation, passes validation
- **Medium (0.7-0.9):** Inferred or paraphrased, contextually correct
- **Low (<0.7):** Ambiguous or multiple possible values
- **None (0.0):** Field not found in document

#### Citation Extraction
**Enhanced Citation System:**
```python
class Citation(BaseModel):
    page_number: int
    section_title: Optional[str]  # e.g., "Article 5: Payment Terms"
    paragraph_index: int  # 0-indexed paragraph on page
    text_snippet: str  # 100 chars before/after match
    start_char: int  # Character offset in full document
    end_char: int
    match_type: Literal["exact", "semantic", "inferred"]

def extract_citation(doc: Document, field_value: str) -> List[Citation]:
    """
    Advanced citation extraction with PDF coordinate tracking
    """
    citations = []
    
    # Method 1: Exact text match
    for page_num, page_text in enumerate(doc.pages):
        if field_value in page_text:
            snippet = extract_context(page_text, field_value, window=100)
            section = find_nearest_heading(page_text, field_value)
            citations.append(Citation(
                page_number=page_num + 1,
                section_title=section,
                text_snippet=snippet,
                match_type="exact"
            ))
    
    # Method 2: Semantic similarity for paraphrased content
    if not citations:
        similar_passages = find_similar_text(doc, field_value, threshold=0.85)
        for passage in similar_passages:
            citations.append(Citation(
                page_number=passage.page,
                text_snippet=passage.text,
                match_type="semantic"
            ))
    
    return citations
```

**UI Features:**
- Clickable citations that highlight source text
- Thumbnail preview of cited page
- "Jump to source" button opens PDF viewer at exact location

---

## 🛡️ AI Reliability & Error Handling

### Handling AI Failures

#### Retry Logic with Exponential Backoff
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type(RateLimitError)
)
async def extract_with_retry(doc_id: str, field_template: dict):
    """Retry extraction on transient failures"""
    try:
        result = await gemini_client.extract(doc_id, field_template)
        return result
    except RateLimitError:
        logger.warning(f"Rate limit hit for doc {doc_id}, retrying...")
        raise  # Trigger retry
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        # Fallback to Groq API
        return await groq_client.extract(doc_id, field_template)
```

#### Graceful Degradation
```python
class ExtractionStrategy:
    """Fallback chain for AI extraction"""
    
    async def extract(self, document: Document) -> ExtractedRecord:
        strategies = [
            ("Gemini 1.5 Flash", self.gemini_extract),
            ("Groq Llama 3.1", self.groq_extract),
            ("Rule-based extraction", self.regex_extract),
        ]
        
        for strategy_name, extract_fn in strategies:
            try:
                result = await extract_fn(document)
                result.extraction_method = strategy_name
                return result
            except Exception as e:
                logger.warning(f"{strategy_name} failed: {e}")
                continue
        
        # All strategies failed
        return ExtractedRecord(
            status="FAILED",
            error="All extraction methods exhausted"
        )
```

### Quality Checks

#### Post-Extraction Validation
```python
def validate_extraction(extracted: ExtractedRecord) -> ValidationResult:
    """Sanity checks after AI extraction"""
    issues = []
    
    # Check 1: Required fields present
    required_fields = get_required_fields(extracted.field_template)
    missing = [f for f in required_fields if not extracted.has_field(f)]
    if missing:
        issues.append(f"Missing required fields: {missing}")
    
    # Check 2: Date logic (effective_date < end_date)
    if extracted.has("effective_date") and extracted.has("end_date"):
        if parse_date(extracted.effective_date) > parse_date(extracted.end_date):
            issues.append("Effective date is after end date")
            extracted.confidence("effective_date") *= 0.5  # Reduce confidence
    
    # Check 3: Currency format validation
    if extracted.has("contract_value"):
        if not is_valid_currency(extracted.contract_value):
            issues.append("Invalid currency format")
    
    # Check 4: Cross-field consistency
    parties = extracted.get("parties", "")
    if "signature" in extracted.fields:
        # Check if signatories match party names
        if not parties_match_signatures(parties, extracted.signature):
            issues.append("Parties don't match signature block")
    
    return ValidationResult(
        is_valid=len(issues) == 0,
        issues=issues,
        needs_human_review=len(issues) > 2
    )
```

#### Confidence Threshold Actions
```python
# Auto-route low confidence fields for human review
LOW_CONFIDENCE_THRESHOLD = 0.7

async def post_extraction_routing(record: ExtractedRecord):
    """Automatically flag fields needing review"""
    for field in record.extracted_fields:
        if field.confidence < LOW_CONFIDENCE_THRESHOLD:
            # Create review task
            await create_review_task(
                field_id=field.id,
                priority="HIGH" if field.is_required else "NORMAL",
                reason=f"Low confidence: {field.confidence:.2f}"
            )
            
            # Send notification
            await notify_reviewer(
                message=f"Field '{field.name}' needs review",
                document=record.document_id
            )
```

### Rate Limit Management

#### Smart Request Batching
```python
class RateLimitedExtractor:
    """Manage API rate limits for free tier"""
    
    def __init__(self):
        self.daily_limit = 1500  # Gemini free tier
        self.requests_today = 0
        self.reset_time = datetime.now() + timedelta(days=1)
    
    async def extract_batch(self, documents: List[Document]):
        """Process documents respecting rate limits"""
        remaining = self.daily_limit - self.requests_today
        
        if remaining <= 0:
            # Wait until reset or use fallback
            wait_seconds = (self.reset_time - datetime.now()).seconds
            if wait_seconds < 3600:  # Less than 1 hour
                await asyncio.sleep(wait_seconds)
            else:
                # Use Groq fallback
                return await self.groq_extract_batch(documents)
        
        # Process in batches to stay under limit
        batch_size = min(remaining, len(documents))
        processed = await self.gemini_extract_batch(documents[:batch_size])
        self.requests_today += batch_size
        
        # Queue remaining for later
        if len(documents) > batch_size:
            await queue_for_later(documents[batch_size:])
        
        return processed
```

---

## 🎨 Frontend Design

### Pages

#### 1. Project List Page
```
┌─────────────────────────────────────┐
│  Legal Review Dashboard             │
├─────────────────────────────────────┤
│  [+ New Project]                    │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ Q4 Contracts                 │  │
│  │ 15 docs | 12 extracted       │  │
│  │ Last updated: 2h ago         │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

#### 2. Project Detail Page
```
┌─────────────────────────────────────┐
│  Q4 Contracts Review                │
├─────────────────────────────────────┤
│  [Upload Documents] [Edit Template] │
│                                     │
│  Documents (15)                     │
│  ├─ contract_a.pdf ✓ Extracted     │
│  ├─ contract_b.pdf ⏳ Processing   │
│  └─ contract_c.pdf ❌ Failed       │
│                                     │
│  [View Comparison Table →]          │
└─────────────────────────────────────┘
```

#### 3. Review Table Page
```
┌──────────────────────────────────────────────────────┐
│  Document     │ Parties          │ Effective Date    │
├──────────────────────────────────────────────────────┤
│ contract_a    │ Acme Corp        │ 2024-01-15       │
│               │ Confidence: 95%  │ Confidence: 88%  │
│               │ ✓ Confirmed      │ [Edit] [✓]       │
├──────────────────────────────────────────────────────┤
│ contract_b    │ XYZ Ltd          │ Not Found        │
│               │ Confidence: 72%  │ Confidence: 0%   │
│               │ [Edit] [✗]       │ [Manual Add]     │
└──────────────────────────────────────────────────────┘
```

**Features:**
- Sortable columns
- Confidence heatmap (color-coded)
- Inline editing
- Bulk review actions
- Export to CSV/Excel

#### 4. Field Template Editor
```
┌─────────────────────────────────────┐
│  Edit Field Template                │
├─────────────────────────────────────┤
│  Template Name: Contract Standard   │
│                                     │
│  Fields:                            │
│  [+] Parties (TEXT, Required)       │
│  [+] Effective Date (DATE)          │
│  [+] Term (NUMBER, months)          │
│  [+] Payment Terms (TEXT)           │
│                                     │
│  [Save] [Cancel]                    │
│  ⚠️  Saving will re-extract all docs │
└─────────────────────────────────────┘
```

#### 5. Evaluation Report Page
```
┌─────────────────────────────────────┐
│  Evaluation Report                  │
├─────────────────────────────────────┤
│  Overall Accuracy: 87%              │
│  Coverage: 93%                      │
│                                     │
│  Field Breakdown:                   │
│  Parties:        95% ████████████   │
│  Effective Date: 88% ███████████    │
│  Payment Terms:  72% █████████      │
│                                     │
│  [Download Full Report]             │
└─────────────────────────────────────┘
```

### UI Components (shadcn/ui)
- `<DataTable>` - Sortable, filterable table
- `<FileUploader>` - Drag-drop upload
- `<StatusBadge>` - Color-coded status
- `<ProgressBar>` - Task progress
- `<ConfidenceIndicator>` - Visual confidence meter
- `<CitationPopover>` - Hover to see source

---

## 🧪 Testing & Quality Assurance

### Testing Strategy

#### 1. Unit Tests (pytest)
- **Models:** Validation, normalization functions
- **Services:** Extraction logic, field matching
- **Parsers:** PDF/DOCX parsing accuracy

```python
def test_date_normalization():
    assert normalize_date("Jan 15, 2024") == "2024-01-15"
    assert normalize_date("15/01/2024") == "2024-01-15"
```

#### 2. Integration Tests
- **API Tests:** FastAPI TestClient
- **Database:** Test fixtures with SQLAlchemy
- **Celery:** Test async tasks with eager mode

```python
def test_document_upload_flow(client):
    response = client.post("/projects/123/documents/upload", files={"file": pdf})
    assert response.status_code == 202
    task_id = response.json()["task_id"]
    # Poll task status
```

#### 3. E2E Tests (Playwright/Cypress)
- **User Flows:** Upload → Extract → Review → Export
- **UI Interactions:** Table sorting, inline editing

#### 4. Extraction Accuracy Evaluation

**Metrics:**
- **Field-level Accuracy:** `correct_fields / total_fields`
- **Exact Match:** String match after normalization
- **Semantic Match:** Cosine similarity > 0.85
- **Coverage:** `extracted_fields / required_fields`

**Test Dataset:**
- Use `data/` sample files
- Create human-labeled ground truth
- Run evaluation on each commit

**Acceptance Criteria:**
- Accuracy > 85%
- Coverage > 90%
- No critical field misses (parties, dates)

---

## 🚀 Deployment & DevOps

### Docker Compose Setup

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/legal_review
      - REDIS_URL=redis://redis:6379/0
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - postgres
      - redis

  celery_worker:
    build: ./backend
    command: celery -A app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/legal_review
      - REDIS_URL=redis://redis:6379/0
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=legal_review
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Environment Variables
```bash
# .env
GEMINI_API_KEY=your-key-here
GROQ_API_KEY=backup-key
DATABASE_URL=postgresql://user:pass@localhost:5432/legal_review
REDIS_URL=redis://localhost:6379/0
AWS_S3_BUCKET=legal-docs  # for production
```

### CI/CD Pipeline (GitHub Actions)
```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose up -d postgres redis
          pytest backend/tests
      - name: Lint
        run: |
          ruff check .
          mypy backend/
```

---

## 📚 Technical Specifications

### Backend Stack
- **Framework:** FastAPI 0.104+
- **ORM:** SQLAlchemy 2.0 (async)
- **Migration:** Alembic
- **Task Queue:** Celery + Redis
- **Validation:** Pydantic v2
- **Testing:** pytest, pytest-asyncio

### Frontend Stack
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript 5+
- **Styling:** Tailwind CSS 3.4
- **Components:** shadcn/ui
- **State:** React Query (TanStack Query) + Zustand
- **Forms:** react-hook-form + zod

### AI/ML Stack
- **LLM:** Google Gemini 1.5 Flash
- **Orchestration:** LangChain
- **Parsers:** PyPDF2, python-docx, BeautifulSoup4, lxml
- **NLP (optional):** spaCy for entity recognition

### Database
- **Primary:** PostgreSQL 15+
- **Schema:** See Data Model section
- **Indexes:** Document project_id, extraction document_id

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Storage:** Local filesystem (MVP), S3 (production)
- **Monitoring:** FastAPI built-in /health endpoint
- **Logging:** structlog

---

## 🔐 Security & Compliance

### Data Security
- **Document Storage:** Encrypted at rest (S3 encryption)
- **API Security:** CORS configuration, rate limiting
- **Secrets:** Environment variables, never committed to git

### Privacy
- **PII Handling:** Legal documents may contain sensitive data
- **Audit Logs:** Track all manual edits and reviews
- **Data Retention:** Configurable deletion policies

### Compliance Considerations
- **GDPR:** Right to deletion, data export
- **SOC 2:** Audit trails for all extraction and reviews
- **Encryption:** TLS 1.3 for all API calls

---

## 📈 Performance Requirements

### Scalability Targets
- **Concurrent Users:** 10-50 (internal tool)
- **Documents:** 1000+ per project
- **Extraction Speed:** <30s per document (10-page contract)
- **Table Load Time:** <2s for 50 documents

### Optimization Strategies
- **Caching:** Redis for parsed documents, template configs
- **Pagination:** Limit table rows to 50, load more on scroll
- **Async Processing:** All extraction/parsing in background
- **Database Indexes:** Compound indexes on foreign keys

---

## 🛣️ Roadmap & Milestones

### Phase 1: MVP (Weeks 1-2)
- ✅ Basic project CRUD
- ✅ Document upload + parsing
- ✅ Simple field extraction (hardcoded template)
- ✅ Display extraction results in table
- ✅ Manual review (confirm/reject)

### Phase 2: Core Features (Weeks 3-4)
- ✅ Custom field templates
- ✅ Async extraction with status tracking
- ✅ Citation extraction
- ✅ Confidence scoring
- ✅ Export to CSV

### Phase 3: Quality & Evaluation (Week 5)
- ✅ Evaluation metrics
- ✅ Ground truth comparison
- ✅ Accuracy reporting
- ✅ Template versioning + re-extraction

### Phase 4: Polish & Deploy (Week 6)
- ✅ Docker Compose setup
- ✅ Error handling + retry logic
- ✅ UI polish (confidence colors, sorting)
- ✅ Documentation + README

### Future Enhancements
- 🔮 Diff highlighting across documents
- 🔮 Annotation layer with comments
- 🔮 Multi-user collaboration
- 🔮 Advanced analytics dashboard
- 🔮 Slack/email notifications

---

## 📋 Acceptance Criteria Summary

### Documentation ✅
- [x] All 8 scope areas covered
- [x] API endpoints explained
- [x] Data structures mapped to system design

### Functional Requirements ✅
- [x] Workflow: upload → parse → configure → extract → review → evaluate
- [x] Each field includes: value + citations + confidence + normalization
- [x] Template updates trigger re-extraction

### Review & Auditability ✅
- [x] Manual edits preserved alongside AI results
- [x] Review status transitions described

### Quality Evaluation ✅
- [x] AI vs human comparison method
- [x] Numeric scores + qualitative notes

### Non-Functional Requirements ✅
- [x] Async processing + status tracking
- [x] Error handling + regeneration logic

### Frontend UX ✅
- [x] All core workflows described
- [x] UI mockups provided

---

## 📞 Support & Contact

**Project Repository:** GitHub (internal)  
**Documentation:** `/docs` folder  
**Issues:** GitHub Issues  
**Questions:** Team Slack #legal-review

---

**Last Updated:** February 3, 2025  
**Next Review:** After Phase 1 completion
