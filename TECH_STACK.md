# Tech Stack & Setup Guide

**Project:** Legal Tabular Review System  
**Last Updated:** February 3, 2025  
**Status:** Ready for Development

---

## 🎯 Final Tech Stack Decisions

### Backend Stack

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| **Framework** | FastAPI | 0.104+ | Modern async support, auto API docs, great for AI integration |
| **Language** | Python | 3.11+ | Rich ecosystem for AI/ML, document processing |
| **Database** | PostgreSQL | 15+ | JSONB support, robust, good for structured+unstructured data |
| **ORM** | SQLAlchemy | 2.0 | Async support, powerful relationships, migrations with Alembic |
| **Task Queue** | Celery | 5.3+ | Async document processing, reliable, Redis backend |
| **Cache/Broker** | Redis | 7+ | Fast, used for Celery + caching parsed documents |
| **Validation** | Pydantic | 2.0+ | Type-safe models, auto validation, FastAPI integration |
| **Testing** | pytest | 7+ | Standard Python testing, async support with pytest-asyncio |

### AI/LLM Stack

| Component | Technology | Free Tier | Notes |
|-----------|-----------|-----------|-------|
| **Primary LLM** | Google Gemini 1.5 Flash | ✅ 1500 req/day | Long context (1M tokens), structured output, FREE |
| **Fallback** | Groq API (Llama 3.1) | ✅ Limited | Fast inference, free tier available |
| **Local Option** | Ollama (Llama 3.1) | ✅ Unlimited | Requires 16GB+ RAM, slower, fully local |
| **Orchestration** | LangChain | ✅ Open source | Prompt management, structured output parsing |
| **Embeddings** | sentence-transformers | ✅ Open source | For semantic similarity in evaluation (optional) |

### Document Processing

| File Type | Library | Version | Purpose |
|-----------|---------|---------|---------|
| **PDF** | PyPDF2 + pdfplumber | Latest | Text extraction, page boundaries |
| **DOCX** | python-docx | Latest | Word document parsing |
| **HTML** | BeautifulSoup4 | 4.12+ | HTML parsing, text extraction |
| **TXT** | Built-in | - | Plain text (trivial) |

### Frontend Stack

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| **Framework** | Next.js | 14+ | SSR, App Router, TypeScript support, production-ready |
| **Language** | TypeScript | 5+ | Type safety, better DX, fewer bugs |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first, fast development, customizable |
| **Components** | shadcn/ui | Latest | Beautiful components, customizable, accessible |
| **State (Server)** | TanStack Query (React Query) | 5+ | Server state caching, auto-refetch, optimistic updates |
| **State (Client)** | Zustand | 4+ | Simple, lightweight, TypeScript-friendly |
| **Forms** | react-hook-form + zod | Latest | Type-safe validation, great UX |
| **HTTP Client** | Axios | 1.6+ | Interceptors, better error handling than fetch |

### DevOps & Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker + Docker Compose | Development & deployment consistency |
| **CI/CD** | GitHub Actions | Automated testing, linting, builds |
| **Logging** | structlog | Structured JSON logs for debugging |
| **Linting (Python)** | ruff + mypy | Fast linting, type checking |
| **Linting (JS/TS)** | ESLint + Prettier | Code quality, formatting |
| **Storage (Dev)** | Local filesystem | Simple file storage |
| **Storage (Prod)** | AWS S3 / MinIO | Object storage for documents (future) |

---

## 📦 Detailed Dependencies

### Backend (requirements.txt)

```txt
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
alembic==1.13.0

# Task Queue
celery[redis]==5.3.4
redis==5.0.1

# AI/LLM
langchain==0.1.0
langchain-google-genai==0.0.6
google-generativeai==0.3.1
sentence-transformers==2.2.2  # optional, for embeddings

# Document Processing
PyPDF2==3.0.1
pdfplumber==0.10.3
python-docx==1.1.0
beautifulsoup4==4.12.2
lxml==4.9.3

# Utilities
python-multipart==0.0.6  # file uploads
python-jose[cryptography]==3.3.0  # JWT (future)
passlib[bcrypt]==1.7.4  # password hashing (future)
python-dotenv==1.0.0

# Logging
structlog==23.2.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2  # FastAPI test client

# Dev Tools
ruff==0.1.8
mypy==1.7.1
black==23.12.0
```

### Frontend (package.json)

```json
{
  "name": "legal-review-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest"
  },
  "dependencies": {
    "next": "14.0.4",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "typescript": "5.3.3",
    
    "@tanstack/react-query": "5.17.0",
    "zustand": "4.4.7",
    
    "axios": "1.6.2",
    "zod": "3.22.4",
    "react-hook-form": "@hookform/resolvers": "3.3.2",
    
    "tailwindcss": "3.4.0",
    "class-variance-authority": "0.7.0",
    "clsx": "2.0.0",
    "tailwind-merge": "2.2.0",
    
    "@radix-ui/react-dialog": "1.0.5",
    "@radix-ui/react-popover": "1.0.7",
    "@radix-ui/react-select": "2.0.0",
    "@radix-ui/react-toast": "1.1.5",
    "lucide-react": "0.303.0"
  },
  "devDependencies": {
    "@types/node": "20.10.6",
    "@types/react": "18.2.46",
    "@types/react-dom": "18.2.18",
    "eslint": "8.56.0",
    "eslint-config-next": "14.0.4",
    "prettier": "3.1.1",
    "prettier-plugin-tailwindcss": "0.5.9",
    "jest": "29.7.0",
    "@testing-library/react": "14.1.2",
    "@testing-library/jest-dom": "6.1.5"
  }
}
```

---

## 🚀 Quick Start Guide

### Prerequisites

Before starting, ensure you have:

- **Docker Desktop** (for Windows/Mac) or Docker Engine (Linux)
- **Node.js** 18+ and npm
- **Python** 3.11+
- **Git**
- **Google Gemini API Key** (FREE - get from https://ai.google.dev/)

### Getting API Keys

#### 1. Google Gemini API (Primary - FREE)
```bash
# Visit: https://ai.google.dev/
# Click "Get API Key in Google AI Studio"
# Create new API key
# Copy key to .env file
```

**Free Tier Limits:**
- 1500 requests per day
- 1 million tokens per request (huge!)
- Perfect for development

#### 2. Groq API (Fallback - FREE)
```bash
# Visit: https://console.groq.com/
# Sign up with Google/GitHub
# Create API key
# Copy to .env as GROQ_API_KEY
```

**Free Tier:**
- Fast Llama 3.1 inference
- Rate limits apply
- Good backup option

---

### Step 1: Clone and Setup

```bash
# Clone repository
cd /path/to/legal-tabular-review-main

# Create .env file
cat > .env << 'EOF'
# AI/LLM
GEMINI_API_KEY=your-gemini-key-here
GROQ_API_KEY=your-groq-key-here  # optional backup

# Database
DATABASE_URL=postgresql://legal_user:legal_pass@postgres:5432/legal_review
POSTGRES_USER=legal_user
POSTGRES_PASSWORD=legal_pass
POSTGRES_DB=legal_review

# Redis
REDIS_URL=redis://redis:6379/0

# Backend
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Environment
ENVIRONMENT=development
EOF

# Make .env.example for others
cp .env .env.example
```

---

### Step 2: Start with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services will be available at:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

### Step 3: Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Optional: Seed sample data
docker-compose exec backend python scripts/seed_data.py
```

---

### Step 4: Verify Installation

```bash
# Check backend health
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# Check frontend
open http://localhost:3000
# Should see project list page

# Check Celery worker
docker-compose logs celery_worker
# Should see "ready" message
```

---

## 🛠️ Development Workflow

### Backend Development

```bash
# Without Docker (local development)
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# Start Celery worker (separate terminal)
celery -A app.workers.celery_app worker --loglevel=info

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Lint
ruff check .
mypy app/
```

### Frontend Development

```bash
# Without Docker (local development)
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# Opens at http://localhost:3000

# Run tests
npm test

# Run linting
npm run lint

# Build for production
npm run build
npm start
```

---

## 🐳 Docker Compose Configuration

### Full docker-compose.yml

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: legal-review-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis (Cache + Celery Broker)
  redis:
    image: redis:7-alpine
    container_name: legal-review-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: legal-review-backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      GROQ_API_KEY: ${GROQ_API_KEY}
      ENVIRONMENT: ${ENVIRONMENT}
    volumes:
      - ./backend:/app
      - ./data:/data  # Document storage
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Celery Worker
  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: legal-review-celery
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      GROQ_API_KEY: ${GROQ_API_KEY}
    volumes:
      - ./backend:/app
      - ./data:/data
    depends_on:
      - postgres
      - redis
    command: celery -A app.workers.celery_app worker --loglevel=info --concurrency=2

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: legal-review-frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL}
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - backend
    command: npm run dev

volumes:
  postgres_data:
```

### Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Default command
CMD ["npm", "run", "dev"]
```

---

## 🧪 Testing Setup

### Backend Testing

```bash
# Create test database
docker-compose exec postgres psql -U legal_user -c "CREATE DATABASE legal_review_test;"

# Run tests with coverage
docker-compose exec backend pytest --cov=app --cov-report=html --cov-report=term

# View coverage report
open backend/htmlcov/index.html
```

### Frontend Testing

```bash
# Run Jest tests
docker-compose exec frontend npm test

# Run with coverage
docker-compose exec frontend npm test -- --coverage

# E2E tests (future)
docker-compose exec frontend npx playwright test
```

---

## 📊 Monitoring & Debugging

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U legal_user -d legal_review

# Common queries
SELECT * FROM projects;
SELECT * FROM documents WHERE upload_status='FAILED';
```

### Redis Access

```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli

# Check keys
KEYS *

# Check Celery tasks
LLEN celery
```

### Celery Flower (Task Monitor)

```bash
# Add to docker-compose.yml
flower:
  build: ./backend
  command: celery -A app.workers.celery_app flower --port=5555
  ports:
    - "5555:5555"
  depends_on:
    - redis

# Access at http://localhost:5555
```

---

## 🔧 Common Issues & Troubleshooting

### Issue: Gemini API Quota Exceeded
**Solution:**
```python
# Switch to Groq fallback in app/services/extractor.py
if gemini_quota_exceeded:
    return use_groq_extractor()
```

### Issue: Celery Tasks Not Running
**Troubleshooting:**
```bash
# Check Redis connection
docker-compose exec celery_worker python -c "import redis; r=redis.from_url('redis://redis:6379/0'); print(r.ping())"

# Check Celery logs
docker-compose logs celery_worker

# Restart worker
docker-compose restart celery_worker
```

### Issue: Database Connection Failed
**Solution:**
```bash
# Check if postgres is running
docker-compose ps postgres

# Check connection
docker-compose exec backend python -c "from app.db.session import engine; print(engine.connect())"

# Restart postgres
docker-compose restart postgres
```

### Issue: Port Already in Use
**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or change port in docker-compose.yml
```

---

## 🎨 Code Style & Best Practices

### Python (Backend)
- **Formatting:** Black (line length 88)
- **Linting:** Ruff (replaces flake8, isort, etc.)
- **Type Checking:** mypy
- **Docstrings:** Google style

### TypeScript (Frontend)
- **Formatting:** Prettier
- **Linting:** ESLint (Next.js config)
- **Naming:** camelCase for variables, PascalCase for components

### Git Workflow
```bash
# Feature branch
git checkout -b feature/extraction-citations

# Commit messages
git commit -m "feat: add citation extraction to LLM prompt"
git commit -m "fix: handle PDF parsing errors gracefully"
git commit -m "docs: update API documentation for review endpoints"

# Conventional commits: feat, fix, docs, test, refactor, chore
```

---

## 📚 Useful Resources

### Documentation
- **FastAPI:** https://fastapi.tiangolo.com/
- **LangChain:** https://python.langchain.com/
- **Gemini API:** https://ai.google.dev/tutorials/python_quickstart
- **Next.js:** https://nextjs.org/docs
- **shadcn/ui:** https://ui.shadcn.com/

### Tutorials
- **Legal Document AI:** https://cloud.google.com/document-ai/docs/
- **PDF Extraction:** https://pypdf2.readthedocs.io/
- **Celery Guide:** https://docs.celeryq.dev/

### Community
- **FastAPI Discord:** https://discord.gg/fastapi
- **LangChain Discord:** https://discord.gg/langchain

---

## 🚀 Next Steps

1. ✅ Read PRD.md (understand requirements)
2. ✅ Read TODO.md (implementation plan)
3. ⬜ Setup development environment (this guide)
4. ⬜ Get Gemini API key
5. ⬜ Start Phase 1: Environment Setup (TODO.md)

---

**Last Updated:** February 3, 2025  
**Maintainer:** Development Team  
**Questions:** Open GitHub issue or Slack #legal-review
