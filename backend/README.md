# Legal Tabular Review - Backend

**FastAPI Backend for AI-Powered Legal Document Extraction**

---

## 🎯 Overview

This is the **backend API service** for the Legal Tabular Review system. It provides RESTful endpoints for document management, AI-powered extraction, and review workflows.

**Key Features:**
- 📄 Multi-format document parsing (PDF, DOCX, HTML, TXT)
- 🤖 Google Gemini AI integration for field extraction
- ⚡ Async task processing with Celery
- 🗄️ PostgreSQL database with SQLAlchemy ORM
- 📊 Confidence scoring + source citations
- ✅ Review workflow management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           FastAPI Application               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │   API    │  │ Services │  │ Workers  │ │
│  │Endpoints │→ │ Business │→ │ Celery   │ │
│  │  (REST)  │  │  Logic   │  │  Tasks   │ │
│  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────┘
         ↓              ↓              ↓
┌──────────────┐  ┌──────────┐  ┌──────────┐
│  PostgreSQL  │  │  Redis   │  │  Gemini  │
│  (Database)  │  │ (Queue)  │  │   API    │
└──────────────┘  └──────────┘  └──────────┘
```

---

## 📂 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   │
│   ├── api/v1/
│   │   ├── router.py              # Main API router
│   │   └── endpoints/
│   │       ├── projects.py        # Project CRUD
│   │       ├── documents.py       # Document upload/download
│   │       ├── field_templates.py # Template management
│   │       ├── extraction.py      # AI extraction endpoints
│   │       └── review.py          # Review workflow
│   │
│   ├── services/
│   │   ├── document_parser.py     # Multi-format parser (314 lines)
│   │   └── extractor.py           # Gemini AI extractor (483 lines)
│   │
│   ├── workers/
│   │   ├── celery_app.py          # Celery configuration
│   │   └── tasks.py               # Background tasks (250 lines)
│   │
│   ├── models/
│   │   └── __init__.py            # SQLAlchemy models
│   │
│   ├── schemas/
│   │   └── __init__.py            # Pydantic schemas
│   │
│   ├── db/
│   │   ├── session.py             # Database session management
│   │   └── __init__.py
│   │
│   ├── core/
│   │   ├── config.py              # Application configuration
│   │   └── __init__.py
│   │
│   └── utils/
│       └── __init__.py            # Utility functions
│
├── alembic/
│   ├── env.py                     # Alembic environment
│   ├── versions/                  # Database migrations
│   └── alembic.ini                # Alembic config
│
├── tests/
│   └── (test files)
│
├── Dockerfile                     # Docker image definition
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# From project root
cd legal-tabular-review

# Start backend + dependencies
docker-compose up backend postgres redis celery_worker

# Backend runs at http://localhost:8004
# API docs at http://localhost:8004/docs
```

### Option 2: Local Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=your-key-here
export DATABASE_URL=postgresql+asyncpg://legal_user:legal_pass@localhost:5436/legal_review
export REDIS_URL=redis://localhost:6383/0

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# In separate terminal: Start Celery worker
celery -A app.workers.celery_app worker --loglevel=info
```

---

## 🔌 API Endpoints

### **Projects**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/projects` | List all projects |
| `POST` | `/api/v1/projects` | Create new project |
| `GET` | `/api/v1/projects/{id}` | Get project details |
| `PUT` | `/api/v1/projects/{id}` | Update project |
| `DELETE` | `/api/v1/projects/{id}` | Delete project |

### **Documents**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/projects/{id}/documents/upload` | Upload document |
| `GET` | `/api/v1/projects/{id}/documents` | List documents |
| `GET` | `/api/v1/documents/{id}` | Get document details |
| `GET` | `/api/v1/documents/{id}/download` | Download file |
| `DELETE` | `/api/v1/documents/{id}` | Delete document |

### **Field Templates**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/field-templates` | List templates |
| `POST` | `/api/v1/field-templates` | Create template |
| `GET` | `/api/v1/field-templates/{id}` | Get template |
| `PUT` | `/api/v1/field-templates/{id}` | Update template |
| `DELETE` | `/api/v1/field-templates/{id}` | Delete template |

### **Extraction**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/documents/{id}/extract` | Extract single document |
| `POST` | `/api/v1/projects/{id}/extract-all` | Extract all documents |
| `GET` | `/api/v1/documents/{id}/extractions` | List extractions |
| `GET` | `/api/v1/extractions/{id}` | Get extraction record |

### **Review**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/reviews` | Create/update review |
| `POST` | `/api/v1/reviews/bulk` | Bulk review operations |
| `GET` | `/api/v1/extractions/{id}/reviews` | List reviews |
| `GET` | `/api/v1/projects/{id}/review-table` | **Get review table data** ⭐ |

---

## 📦 Tech Stack

- **Framework:** FastAPI 0.104+
- **Database:** PostgreSQL 15 + SQLAlchemy 2.0 (async)
- **Task Queue:** Celery 5.3 + Redis 7
- **AI/LLM:** Google Gemini 1.5 Flash via LangChain
- **Document Parsing:** PyPDF2, python-docx, BeautifulSoup4
- **Testing:** pytest + pytest-asyncio
- **Logging:** structlog (JSON logs)

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_document_parser.py

# View coverage report
open htmlcov/index.html
```

---

## 📄 License

MIT License

---

**Built with FastAPI + Google Gemini 🚀**
