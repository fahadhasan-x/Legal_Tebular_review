# Legal Tabular Review - Implementation TODO

**Status:** Planning Complete → Ready for Development  
**Last Updated:** February 3, 2025  
**Development Timeline:** 6 weeks (MVP → Production)

---

## 🎯 Overview

This TODO document breaks down the PRD into actionable development tasks organized by phase. Each task includes acceptance criteria and estimated effort.

**Legend:**
- 🟢 **Easy** (1-4 hours)
- 🟡 **Medium** (4-8 hours)
- 🔴 **Hard** (1-2 days)
- ⚫ **Complex** (2-5 days)

**Status:**
- ⬜ Not started
- 🔄 In progress
- ✅ Complete
- ❌ Blocked

---

## Phase 1: MVP Foundation (Week 1-2)
**Goal:** Basic document upload → extraction → table display

### 1.1 Development Environment Setup

#### ⬜ 1.1.1 Initialize Docker Compose Environment 🟡
**Effort:** 6h  
**Tasks:**
- [ ] Create `docker-compose.yml` with services: postgres, redis, backend, frontend
- [ ] Configure environment variables template (`.env.example`)
- [ ] Setup PostgreSQL with initial database
- [ ] Setup Redis for caching and Celery
- [ ] Test docker-compose up and verify all services running
- [ ] Write quick-start guide in README

**Acceptance:**
- `docker-compose up` starts all services without errors
- PostgreSQL accessible at `localhost:5432`
- Redis accessible at `localhost:6379`
- Backend health check at `localhost:8000/health` returns 200

---

#### ⬜ 1.1.2 Backend Project Structure 🟢
**Effort:** 3h  
**Tasks:**
- [ ] Create FastAPI project structure:
  ```
  backend/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── config.py
  │   ├── api/
  │   │   ├── __init__.py
  │   │   ├── v1/
  │   │   │   ├── endpoints/
  │   │   │   │   ├── projects.py
  │   │   │   │   ├── documents.py
  │   │   │   │   ├── extraction.py
  │   │   │   │   └── review.py
  │   │   │   └── router.py
  │   ├── models/
  │   │   ├── project.py
  │   │   ├── document.py
  │   │   └── extraction.py
  │   ├── schemas/
  │   │   └── pydantic models
  │   ├── services/
  │   │   ├── document_parser.py
  │   │   ├── extractor.py
  │   │   └── review.py
  │   ├── db/
  │   │   ├── base.py
  │   │   └── session.py
  │   ├── workers/
  │   │   └── celery_app.py
  │   └── utils/
  └── tests/
  ```
- [ ] Setup dependencies: FastAPI, SQLAlchemy, Celery, Pydantic
- [ ] Configure logging with structlog
- [ ] Add CORS middleware

**Acceptance:**
- FastAPI server runs at `localhost:8000`
- `/docs` shows Swagger UI
- `/health` endpoint returns server status

---

#### ⬜ 1.1.3 Frontend Project Structure 🟢
**Effort:** 3h  
**Tasks:**
- [ ] Create Next.js 14 project with TypeScript
- [ ] Install dependencies: Tailwind, shadcn/ui, React Query, Zustand
- [ ] Setup project structure:
  ```
  frontend/
  ├── src/
  │   ├── app/
  │   │   ├── layout.tsx
  │   │   ├── page.tsx
  │   │   ├── projects/
  │   │   └── review/
  │   ├── components/
  │   │   ├── ui/  (shadcn)
  │   │   ├── FileUploader.tsx
  │   │   ├── DataTable.tsx
  │   │   └── StatusBadge.tsx
  │   ├── lib/
  │   │   ├── api-client.ts
  │   │   └── utils.ts
  │   └── types/
  │       └── index.ts
  └── public/
  ```
- [ ] Configure Tailwind CSS
- [ ] Setup API client with axios/fetch

**Acceptance:**
- Next.js dev server runs at `localhost:3000`
- Tailwind styling works
- API client can call backend health endpoint

---

### 1.2 Database & Models

#### ⬜ 1.2.1 Database Schema Implementation ⚫
**Effort:** 2 days  
**Tasks:**
- [ ] Create SQLAlchemy models matching PRD schema:
  - `Project` model
  - `FieldTemplate` model
  - `Document` model
  - `ExtractedRecord` model
  - `ReviewRecord` model
  - `EvaluationResult` model
- [ ] Define relationships (ForeignKey, backref)
- [ ] Add indexes for performance
- [ ] Create Alembic migration scripts
- [ ] Seed initial field template (Standard Contract)

**Acceptance:**
- `alembic upgrade head` creates all tables
- Relationships work (e.g., Project → Documents)
- Indexes exist on foreign keys
- Sample template inserted successfully

---

#### ⬜ 1.2.2 Pydantic Schemas 🟡
**Effort:** 4h  
**Tasks:**
- [ ] Create request/response schemas for all models
- [ ] Add validation rules (field types, required fields)
- [ ] Implement DTOs (Data Transfer Objects)
- [ ] Add examples for Swagger docs

**Example:**
```python
class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    field_template_id: Optional[UUID] = None

class ProjectResponse(BaseModel):
    id: UUID
    name: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

**Acceptance:**
- All CRUD operations have request/response schemas
- Validation catches invalid inputs
- Swagger docs show schema examples

---

### 1.3 Core API Endpoints

#### ⬜ 1.3.1 Project CRUD Endpoints 🟡
**Effort:** 6h  
**Tasks:**
- [ ] `POST /api/v1/projects` - Create project
- [ ] `GET /api/v1/projects` - List all projects
- [ ] `GET /api/v1/projects/{id}` - Get project details
- [ ] `PUT /api/v1/projects/{id}` - Update project
- [ ] `DELETE /api/v1/projects/{id}` - Delete project (soft delete)
- [ ] Add pagination for list endpoint
- [ ] Add filtering by status

**Acceptance:**
- All endpoints return correct status codes
- CRUD operations persist to database
- Pagination works (limit/offset)
- Invalid UUIDs return 404

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project"}'
```

---

#### ⬜ 1.3.2 Document Upload Endpoint 🔴
**Effort:** 1 day  
**Tasks:**
- [ ] `POST /api/v1/projects/{id}/documents/upload` - Upload file
- [ ] Support multipart/form-data
- [ ] Validate file types (PDF, DOCX, HTML, TXT)
- [ ] Validate file size (max 50MB)
- [ ] Save file to local storage (`/data/uploads/{project_id}/`)
- [ ] Create Document record in database
- [ ] Trigger async parsing task (Celery)
- [ ] Return task_id for status tracking

**Acceptance:**
- PDF upload creates Document record
- File saved to correct path
- Celery task enqueued
- Unsupported file types rejected (400 error)

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/projects/123/documents/upload \
  -F "file=@contract.pdf"
```

---

### 1.4 Document Parsing

#### ⬜ 1.4.1 PDF Parser Implementation 🟡
**Effort:** 6h  
**Tasks:**
- [ ] Install PyPDF2 and pdfplumber
- [ ] Create `DocumentParser` service class
- [ ] Implement `parse_pdf()` method:
  - Extract text from all pages
  - Preserve page numbers
  - Extract metadata (author, creation date)
- [ ] Handle encrypted PDFs (skip with error message)
- [ ] Handle scanned PDFs (warn user - OCR not supported in MVP)

**Example:**
```python
class DocumentParser:
    def parse_pdf(self, file_path: str) -> ParsedDocument:
        with open(file_path, 'rb') as f:
            pdf = PdfReader(f)
            text = ""
            for i, page in enumerate(pdf.pages):
                text += f"\n--- Page {i+1} ---\n{page.extract_text()}"
        return ParsedDocument(text=text, pages=len(pdf.pages))
```

**Acceptance:**
- Sample PDFs from `data/` folder parsed successfully
- Page boundaries preserved
- Metadata extracted
- Encrypted PDFs return clear error

---

#### ⬜ 1.4.2 DOCX/HTML Parser Implementation 🟢
**Effort:** 4h  
**Tasks:**
- [ ] Install python-docx, BeautifulSoup4
- [ ] Implement `parse_docx()` method
- [ ] Implement `parse_html()` method
- [ ] Implement `parse_txt()` method (trivial)
- [ ] Unified interface for all parsers

**Acceptance:**
- All 4 file types parsed correctly
- Text extracted with reasonable formatting
- Tables and lists handled gracefully

---

#### ⬜ 1.4.3 Celery Task for Parsing ⚫
**Effort:** 2 days  
**Tasks:**
- [ ] Setup Celery with Redis broker
- [ ] Create `parse_document_task(document_id)` Celery task
- [ ] Update Document.upload_status during parsing:
  - `UPLOADED` → `PARSING` → `PARSED` | `FAILED`
- [ ] Store parsed_text in database
- [ ] Handle parsing errors gracefully
- [ ] Add retry logic (3 attempts)
- [ ] Log task progress

**Acceptance:**
- Celery worker picks up task after upload
- Document status updates correctly
- Parsed text stored in database
- Failed parses set status to FAILED with error message

**Test:**
```bash
# Start Celery worker
celery -A app.workers.celery_app worker --loglevel=info
```

---

### 1.5 Basic Extraction (Hardcoded Template)

#### ⬜ 1.5.1 Gemini API Integration 🔴
**Effort:** 1 day  
**Tasks:**
- [ ] Install LangChain and langchain-google-genai
- [ ] Setup Gemini API client
- [ ] Create `.env` with `GEMINI_API_KEY`
- [ ] Implement `GeminiExtractor` service class
- [ ] Test basic prompt → response flow
- [ ] Add error handling (API limits, network errors)
- [ ] Add retry with exponential backoff

**Example:**
```python
from langchain_google_genai import ChatGoogleGenerativeAI

class GeminiExtractor:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            google_api_key=settings.GEMINI_API_KEY
        )
    
    def extract_fields(self, document_text: str, field_template: dict) -> dict:
        prompt = self._build_prompt(document_text, field_template)
        response = self.llm.invoke(prompt)
        return self._parse_response(response)
```

**Acceptance:**
- Gemini API returns valid responses
- API key loaded from environment
- Errors handled gracefully
- Rate limits respected

---

#### ⬜ 1.5.2 Extraction Prompt Engineering 🔴
**Effort:** 1.5 days  
**Tasks:**
- [ ] Design prompt template for field extraction
- [ ] Include field definitions in prompt
- [ ] Request structured JSON output
- [ ] Add examples (few-shot prompting)
- [ ] Test with sample documents from `data/`
- [ ] Iterate on prompt based on results

**Prompt Template:**
```
You are a legal document analyst. Extract the following fields from this contract:

Fields:
1. parties: Names of all contracting parties
2. effective_date: When the contract becomes effective
3. term: Duration of the contract
4. payment_terms: Payment schedule and amounts

Document:
{document_text}

Output JSON format:
{
  "fields": [
    {
      "field_id": "parties",
      "raw_value": "exact text from document",
      "confidence_score": 0.0 to 1.0,
      "citations": [{"source": "page X, section Y", "snippet": "..."}]
    }
  ]
}

If a field is not found, set raw_value to null and confidence to 0.0.
```

**Acceptance:**
- Extraction returns valid JSON
- Fields match template
- Confidence scores reasonable
- Citations include page references

---

#### ⬜ 1.5.3 Structured Output Parsing 🟡
**Effort:** 6h  
**Tasks:**
- [ ] Create Pydantic models for extraction output:
  - `Citation` model
  - `ExtractedField` model
  - `ExtractionResult` model
- [ ] Use LangChain `PydanticOutputParser`
- [ ] Validate extraction output schema
- [ ] Handle malformed JSON from LLM
- [ ] Store extracted fields in `ExtractedRecord` table

**Acceptance:**
- All extraction outputs conform to schema
- Invalid outputs caught and retried
- Parsed data stored correctly in database

---

#### ⬜ 1.5.4 Extraction Celery Task ⚫
**Effort:** 2 days  
**Tasks:**
- [ ] Create `extract_document_task(document_id, template_id)` task
- [ ] Load parsed document text from database
- [ ] Load field template
- [ ] Call Gemini extractor
- [ ] Parse and validate output
- [ ] Store ExtractedRecord in database
- [ ] Update extraction_status (PENDING → IN_PROGRESS → COMPLETED)
- [ ] Handle extraction errors

**Acceptance:**
- Task triggered after document parsing completes
- Extraction results stored in database
- Status updates reflect progress
- Errors logged and status set to FAILED

---

### 1.6 Review Table Frontend

#### ⬜ 1.6.1 Project List Page 🟡
**Effort:** 5h  
**Tasks:**
- [ ] Create `/projects` page
- [ ] Fetch projects from API
- [ ] Display project cards with stats
- [ ] Add "Create Project" button and modal
- [ ] Add navigation to project detail page

**Components:**
- `ProjectCard` - Shows name, doc count, status
- `CreateProjectModal` - Form to create new project

**Acceptance:**
- Projects load from API
- Create project form works
- Clicking project navigates to detail page

---

#### ⬜ 1.6.2 Project Detail Page 🟡
**Effort:** 6h  
**Tasks:**
- [ ] Create `/projects/[id]` page
- [ ] Fetch project details with documents list
- [ ] Display document upload status
- [ ] Add "Upload Documents" button
- [ ] Show extraction progress per document
- [ ] Add "View Review Table" button

**Components:**
- `DocumentList` - Table of uploaded documents
- `FileUploader` - Drag-drop upload component
- `StatusBadge` - Visual status indicator

**Acceptance:**
- Project details load correctly
- Document list shows upload/parsing/extraction status
- Upload works and triggers backend task

---

#### ⬜ 1.6.3 Review Table Component ⚫
**Effort:** 3 days  
**Tasks:**
- [ ] Create `/projects/[id]/review` page
- [ ] Fetch extracted records for all documents
- [ ] Build dynamic table:
  - Rows: Documents
  - Columns: Field template fields
  - Cells: Extracted values with confidence
- [ ] Add sortable columns
- [ ] Add confidence color coding:
  - Green (>0.9)
  - Yellow (0.7-0.9)
  - Red (<0.7)
- [ ] Add hover to show citations
- [ ] Add inline edit for manual updates
- [ ] Add confirm/reject buttons per field

**Components:**
- `ReviewTable` - Main table component
- `ReviewCell` - Individual field cell with actions
- `CitationPopover` - Shows source on hover
- `ConfidenceBar` - Visual confidence indicator

**Acceptance:**
- Table displays all extracted fields
- Sorting works
- Confidence colors correct
- Citations show on hover
- Inline editing updates backend

---

### 1.7 Manual Review Backend

#### ⬜ 1.7.1 Review CRUD Endpoints 🟡
**Effort:** 5h  
**Tasks:**
- [ ] `POST /api/v1/review-records` - Create/update review
- [ ] `GET /api/v1/projects/{id}/review-table` - Get table data
- [ ] Support review actions:
  - CONFIRM (accept AI value)
  - REJECT (mark as incorrect)
  - MANUAL_UPDATE (save edited value)
- [ ] Store manual_value alongside AI value
- [ ] Preserve audit trail (who, when)

**Acceptance:**
- Review actions saved to database
- Manual edits preserved
- Original AI values not overwritten
- Review table endpoint returns combined AI + manual data

---

## Phase 2: Core Features (Week 3-4)
**Goal:** Custom templates, citations, async status, export

### 2.1 Field Template Management

#### ⬜ 2.1.1 Template CRUD Endpoints 🟡
**Effort:** 6h  
**Tasks:**
- [ ] `POST /api/v1/field-templates` - Create template
- [ ] `GET /api/v1/field-templates` - List templates
- [ ] `GET /api/v1/field-templates/{id}` - Get template
- [ ] `PUT /api/v1/field-templates/{id}` - Update template
- [ ] Support field types: TEXT, DATE, NUMBER, BOOLEAN, LIST
- [ ] Add validation rules per field
- [ ] Version templates (increment version on update)

**Acceptance:**
- Templates CRUD operations work
- Field types validated
- Versioning increments correctly

---

#### ⬜ 2.1.2 Template Editor UI 🔴
**Effort:** 1.5 days  
**Tasks:**
- [ ] Create `/field-templates` page
- [ ] Build template editor form:
  - Add/remove fields
  - Set field type
  - Set required/optional
  - Add extraction hints
- [ ] Save template via API
- [ ] Warn user about re-extraction when updating

**Components:**
- `TemplateEditor` - Form builder interface
- `FieldRow` - Individual field configuration
- `FieldTypePicker` - Dropdown for field types

**Acceptance:**
- Create new template works
- Edit existing template works
- Re-extraction warning shows

---

#### ⬜ 2.1.3 Template Update Triggers Re-extraction ⚫
**Effort:** 2 days  
**Tasks:**
- [ ] When template updated, find all projects using it
- [ ] Trigger `re_extract_project_task(project_id)` Celery task
- [ ] Task re-runs extraction for all documents in project
- [ ] Compare new vs old results (audit log)
- [ ] Update ExtractedRecord with new version

**Acceptance:**
- Template update triggers re-extraction
- All documents in affected projects re-processed
- Old and new results preserved for comparison

---

### 2.2 Citation Extraction

#### ⬜ 2.2.1 Enhanced Prompt for Citations 🟡
**Effort:** 4h  
**Tasks:**
- [ ] Update extraction prompt to request citations
- [ ] Ask LLM to include:
  - Page number
  - Section/paragraph reference
  - Text snippet (50 chars before/after)
- [ ] Validate citation format in output

**Acceptance:**
- Citations returned in extraction output
- Citations include page + snippet
- Format consistent

---

#### ⬜ 2.2.2 Citation Storage 🟢
**Effort:** 3h  
**Tasks:**
- [ ] Store citations as JSONB array in ExtractedRecord.extracted_fields
- [ ] Index citation data for search (future)

**Acceptance:**
- Citations persisted to database
- Retrievable via API

---

#### ⬜ 2.2.3 Citation UI Component 🟡
**Effort:** 5h  
**Tasks:**
- [ ] Create `CitationPopover` component
- [ ] Show on hover over field value
- [ ] Display source (page, section)
- [ ] Display text snippet
- [ ] (Future) Link to document viewer at exact location

**Acceptance:**
- Hover shows citation popover
- Citation data readable

---

### 2.3 Async Status Tracking

#### ⬜ 2.3.1 Task Status Endpoint 🟡
**Effort:** 4h  
**Tasks:**
- [ ] `GET /api/v1/tasks/{task_id}/status` - Get Celery task status
- [ ] Return:
  - Task ID
  - Task type (PARSING, EXTRACTION, etc.)
  - Status (PENDING, IN_PROGRESS, COMPLETED, FAILED)
  - Progress (0.0-1.0)
  - Result (if completed)
  - Error (if failed)

**Acceptance:**
- Task status endpoint returns correct state
- Progress updates in real-time
- Completed tasks return results

---

#### ⬜ 2.3.2 Status Polling UI 🟡
**Effort:** 6h  
**Tasks:**
- [ ] Create `useTaskStatus` React hook
- [ ] Poll task status every 2s until completed
- [ ] Show progress bar during processing
- [ ] Show success/error message on completion
- [ ] Auto-refresh data when task completes

**Acceptance:**
- Upload shows progress bar
- Status updates automatically
- UI refreshes when extraction completes

---

### 2.4 Export Functionality

#### ⬜ 2.4.1 CSV Export Endpoint 🟡
**Effort:** 5h  
**Tasks:**
- [ ] `GET /api/v1/projects/{id}/export/csv` - Export table as CSV
- [ ] Generate CSV with:
  - Row per document
  - Column per field
  - Include confidence scores (optional column)
- [ ] Stream response for large datasets

**Acceptance:**
- CSV download works
- Data matches review table
- Opens correctly in Excel

---

#### ⬜ 2.4.2 Export Button UI 🟢
**Effort:** 2h  
**Tasks:**
- [ ] Add "Export CSV" button to review table page
- [ ] Trigger download on click
- [ ] Show loading state during export

**Acceptance:**
- Button triggers CSV download
- File saves to Downloads folder

---

## Phase 3: Quality & Evaluation (Week 5)
**Goal:** Metrics, evaluation, testing

### 3.1 Evaluation System

#### ⬜ 3.1.1 Ground Truth Upload 🟡
**Effort:** 6h  
**Tasks:**
- [ ] `POST /api/v1/projects/{id}/ground-truth` - Upload human labels
- [ ] Accept JSON format:
  ```json
  [
    {"document_id": "uuid", "field_id": "parties", "ground_truth": "Acme Corp, XYZ Ltd"}
  ]
  ```
- [ ] Store in database (new table or JSONB column)

**Acceptance:**
- Ground truth upload works
- Data stored correctly

---

#### ⬜ 3.1.2 Evaluation Metrics Implementation ⚫
**Effort:** 2 days  
**Tasks:**
- [ ] Create `EvaluationService` class
- [ ] Implement metrics:
  - **Exact Match:** String match after normalization
  - **Field Accuracy:** `correct / total`
  - **Coverage:** `extracted / required`
  - **Semantic Match:** Cosine similarity using embeddings (optional)
- [ ] Calculate per-field and overall scores
- [ ] Store results in `EvaluationResult` table

**Acceptance:**
- Metrics calculated correctly
- Results stored in database
- Per-field breakdown available

---

#### ⬜ 3.1.3 Evaluation Report UI 🟡
**Effort:** 6h  
**Tasks:**
- [ ] Create `/projects/{id}/evaluation` page
- [ ] Display metrics:
  - Overall accuracy
  - Coverage
  - Per-field scores
  - Heatmap/chart visualization
- [ ] Add "Download Report" button (PDF/CSV)

**Acceptance:**
- Metrics displayed clearly
- Charts render correctly
- Report download works

---

### 3.2 Testing

#### ⬜ 3.2.1 Backend Unit Tests ⚫
**Effort:** 3 days  
**Tasks:**
- [ ] Write pytest tests for:
  - Document parser (PDF, DOCX, HTML)
  - Extraction service (mocked LLM)
  - Review logic
  - Normalization functions
- [ ] Achieve >80% code coverage
- [ ] Setup pytest fixtures for test data

**Acceptance:**
- `pytest` runs all tests
- Coverage >80%
- CI pipeline green

---

#### ⬜ 3.2.2 API Integration Tests 🔴
**Effort:** 1.5 days  
**Tasks:**
- [ ] Test full workflows:
  - Create project → upload doc → extract → review
- [ ] Use FastAPI TestClient
- [ ] Mock Celery tasks (eager mode)
- [ ] Test error cases (invalid inputs, missing files)

**Acceptance:**
- Integration tests pass
- Error handling verified

---

#### ⬜ 3.2.3 Frontend E2E Tests 🔴
**Effort:** 1 day  
**Tasks:**
- [ ] Setup Playwright/Cypress
- [ ] Test user flows:
  - Create project
  - Upload document
  - View review table
  - Edit field value
- [ ] Test on Chrome, Firefox

**Acceptance:**
- E2E tests pass in CI
- All critical paths covered

---

#### ⬜ 3.2.4 Extraction Accuracy Test 🟡
**Effort:** 6h  
**Tasks:**
- [ ] Create human-labeled test set from `data/` files
- [ ] Run extraction on test set
- [ ] Calculate accuracy metrics
- [ ] Document results in `docs/EVALUATION.md`

**Acceptance:**
- Accuracy >85%
- Coverage >90%
- Results documented

---

## Phase 4: Polish & Deploy (Week 6)
**Goal:** Production-ready system

### 4.1 Error Handling & Resilience

#### ⬜ 4.1.1 Comprehensive Error Handling 🔴
**Effort:** 1 day  
**Tasks:**
- [ ] Add try-except blocks in all services
- [ ] Return user-friendly error messages
- [ ] Log errors with context (structlog)
- [ ] Implement retry logic for LLM calls
- [ ] Handle network failures gracefully

**Acceptance:**
- Errors don't crash server
- Users see helpful error messages
- Errors logged for debugging

---

#### ⬜ 4.1.2 Input Validation 🟡
**Effort:** 4h  
**Tasks:**
- [ ] Validate all API inputs (Pydantic)
- [ ] Check file types and sizes
- [ ] Sanitize user input (SQL injection prevention)
- [ ] Validate UUIDs before database queries

**Acceptance:**
- Invalid inputs rejected with 400 errors
- No security vulnerabilities

---

### 4.2 Performance Optimization

#### ⬜ 4.2.1 Database Indexing 🟢
**Effort:** 3h  
**Tasks:**
- [ ] Add indexes on foreign keys
- [ ] Add composite indexes for common queries
- [ ] Run EXPLAIN ANALYZE on slow queries
- [ ] Optimize N+1 query issues

**Acceptance:**
- Review table loads <2s for 50 documents
- No N+1 queries

---

#### ⬜ 4.2.2 Caching 🟡
**Effort:** 5h  
**Tasks:**
- [ ] Cache parsed documents in Redis
- [ ] Cache field templates
- [ ] Set TTL (1 hour)
- [ ] Invalidate cache on updates

**Acceptance:**
- Repeated requests faster
- Cache hit rate >70%

---

### 4.3 Documentation

#### ⬜ 4.3.1 API Documentation 🟢
**Effort:** 3h  
**Tasks:**
- [ ] Ensure all endpoints have docstrings
- [ ] Add examples to Swagger UI
- [ ] Write API usage guide in `docs/API.md`

**Acceptance:**
- `/docs` shows complete API reference
- Examples help developers

---

#### ⬜ 4.3.2 User Guide 🟡
**Effort:** 4h  
**Tasks:**
- [ ] Write user guide in `docs/USER_GUIDE.md`
- [ ] Add screenshots
- [ ] Cover:
  - Creating projects
  - Uploading documents
  - Reviewing extractions
  - Exporting data

**Acceptance:**
- Non-technical users can follow guide
- Screenshots up-to-date

---

#### ⬜ 4.3.3 Developer Setup Guide 🟡
**Effort:** 3h  
**Tasks:**
- [ ] Update `README.md` with:
  - Prerequisites
  - Installation steps
  - Running with Docker
  - Environment variables
  - Testing instructions
- [ ] Add troubleshooting section

**Acceptance:**
- New developer can setup in <15 minutes
- Docker setup works

---

### 4.4 Deployment

#### ⬜ 4.4.1 Docker Production Build 🟡
**Effort:** 6h  
**Tasks:**
- [ ] Create production Dockerfiles (multi-stage builds)
- [ ] Optimize image sizes
- [ ] Add health checks
- [ ] Configure logging to stdout

**Acceptance:**
- Production images build successfully
- Images <500MB
- Health checks pass

---

#### ⬜ 4.4.2 Environment Configuration 🟢
**Effort:** 3h  
**Tasks:**
- [ ] Document all environment variables
- [ ] Create `.env.example` templates
- [ ] Add validation for required env vars on startup

**Acceptance:**
- All env vars documented
- Missing vars cause startup error with helpful message

---

#### ⬜ 4.4.3 CI/CD Pipeline 🔴
**Effort:** 1 day  
**Tasks:**
- [ ] Setup GitHub Actions workflow
- [ ] Run tests on every PR
- [ ] Build Docker images on main branch
- [ ] Add linting (ruff, mypy, eslint)

**Example `.github/workflows/ci.yml`:**
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start services
        run: docker-compose up -d postgres redis
      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
      - name: Run frontend tests
        run: |
          cd frontend
          npm install
          npm test
```

**Acceptance:**
- CI runs on every commit
- Tests pass before merge
- Linting catches issues

---

## Phase 5: Future Enhancements (Post-MVP)

### 🔮 5.1 Diff Highlighting
**Effort:** 1 week  
- Compute differences across documents for same field
- Highlight changes in UI (green/red highlighting)
- Support clause-level comparison

### 🔮 5.2 Annotation Layer
**Effort:** 1.5 weeks  
- Add comments/notes to specific fields
- Support threaded discussions
- Track annotation history

### 🔮 5.3 Advanced Analytics
**Effort:** 1 week  
- Dashboard with extraction stats over time
- Identify low-confidence fields for review priority
- Track manual edit frequency

### 🔮 5.4 Multi-user Collaboration
**Effort:** 2 weeks  
- User authentication (JWT)
- Role-based access control (admin, reviewer, viewer)
- Real-time updates (WebSockets)

### 🔮 5.5 Document Viewer Integration
**Effort:** 1.5 weeks  
- Embed PDF viewer in UI
- Highlight citation locations in document
- Click citation → jump to source

### 🔮 5.6 Advanced LLM Features
**Effort:** 1 week  
- Multi-model ensemble (Gemini + Groq)
- Confidence calibration
- Active learning (retrain on manual edits)

---

## 📊 Progress Tracking

### Weekly Milestones

**Week 1:** Environment setup, database, basic API  
**Week 2:** Document parsing, basic extraction, review table  
**Week 3:** Custom templates, citations, async status  
**Week 4:** Export, polish extraction, UI improvements  
**Week 5:** Evaluation system, testing, metrics  
**Week 6:** Error handling, optimization, documentation, deployment

### Definition of Done (DoD)
For each task to be considered complete:
- [ ] Code written and tested locally
- [ ] Unit tests pass
- [ ] Code reviewed (if team)
- [ ] Documentation updated
- [ ] No critical bugs
- [ ] Acceptance criteria met

---

## 🚦 Risk Mitigation

### High-Risk Items
1. **LLM Accuracy:** If extraction <85%, try:
   - Better prompt engineering
   - Few-shot examples
   - Switch to Gemini Pro (more expensive)
   - Hybrid rule-based + LLM

2. **Performance:** If table slow, try:
   - Pagination/virtual scrolling
   - Database indexes
   - Caching

3. **PDF Parsing:** If scanned PDFs fail:
   - Add OCR (Tesseract) support
   - Warn users to upload text-based PDFs

### Contingency Plans
- **LLM API limits:** Implement rate limiting + queue
- **Budget concerns:** Switch to free Groq API
- **Time constraints:** Defer Phase 5 features to post-MVP

---

## 📞 Support & Questions

**Blockers:** Create GitHub issue with `blocker` label  
**Questions:** Slack #legal-review channel  
**Code Review:** Tag `@reviewer` in PR

---

**Last Updated:** February 3, 2025  
**Next Review:** After Phase 1 completion
