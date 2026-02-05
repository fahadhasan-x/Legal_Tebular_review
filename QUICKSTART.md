# 🚀 Legal Tabular Review - Quick Start Guide

## ⚡ Fast Setup (5 minutes)

### 1. Prerequisites Check
```bash
# Check Docker
docker --version  # Should be 20.10+
docker-compose --version  # Should be 2.0+

# Check Git
git --version
```

### 2. Get Gemini API Key (FREE!)
1. Visit: https://ai.google.dev/
2. Click "Get API Key in Google AI Studio"
3. Create new API key
4. Copy the key (starts with `AIza...`)

### 3. Clone & Configure
```bash
# Navigate to project
cd legal-tabular-review-main

# Create .env file
cp .env.example .env

# Edit .env and add your Gemini API key
# On Windows: notepad .env
# On Mac/Linux: nano .env

# Change this line:
GEMINI_API_KEY=your-gemini-api-key-here
# To:
GEMINI_API_KEY=AIzaSy...your-actual-key...
```

### 4. Start Everything!
```bash
# Build and start all services (takes 2-3 minutes first time)
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### 5. Access Applications
- **Frontend:** http://localhost:3004
- **Backend API:** http://localhost:8004
- **API Docs:** http://localhost:8004/docs
- **Flower (Celery Monitor):** http://localhost:5559

### 6. Verify Installation
```bash
# Check backend health
curl http://localhost:8004/health

# Expected response:
# {"status":"healthy","environment":"development","version":"1.0.0"}
```

---

## 📊 Port Configuration

**Custom Ports (to avoid conflicts):**
- Frontend: **3004** (default 3000 + 4)
- Backend: **8004** (default 8000 + 4)
- PostgreSQL: **5436** (default 5432 + 4)
- Redis: **6383** (default 6379 + 4)
- Flower: **5559** (default 5555 + 4)

---

## 🔧 Common Commands

### Start/Stop Services
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart specific service
docker-compose restart backend

# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### Database Operations
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "add new field"

# Connect to PostgreSQL
docker-compose exec postgres psql -U legal_user -d legal_review
```

### Development
```bash
# Backend shell
docker-compose exec backend python

# Run backend tests
docker-compose exec backend pytest

# Frontend shell
docker-compose exec frontend sh

# Run frontend dev server
docker-compose exec frontend npm run dev
```

---

## 🐛 Troubleshooting

### Issue: Port Already in Use
```bash
# Find process using port
lsof -i :8004  # Mac/Linux
netstat -ano | findstr :8004  # Windows

# Solution: Change port in docker-compose.yml or kill the process
```

### Issue: Gemini API Error
```bash
# Check if key is set
docker-compose exec backend env | grep GEMINI

# Solution: Verify .env file has correct key
```

### Issue: Database Connection Failed
```bash
# Check if postgres is running
docker-compose ps postgres

# Restart postgres
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Issue: Celery Worker Not Running
```bash
# Check worker logs
docker-compose logs celery_worker

# Restart worker
docker-compose restart celery_worker
```

---

## 🎯 Next Steps

1. ✅ Services running
2. ⬜ Read [TODO.md](../TODO.md) - Phase 1 tasks
3. ⬜ Create first project via API
4. ⬜ Upload sample document
5. ⬜ Test extraction

### Test API with curl:
```bash
# Create project
curl -X POST http://localhost:8004/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project", "description": "My first project"}'

# List projects
curl http://localhost:8004/api/v1/projects
```

---

## 📚 More Help

- **Full Documentation:** [TECH_STACK.md](../TECH_STACK.md)
- **Implementation Tasks:** [TODO.md](../TODO.md)
- **Architecture:** [PRD.md](../PRD.md)

**Questions?** Open a GitHub issue or check the troubleshooting section.

---

**Last Updated:** February 2025  
**Status:** ✅ Backend Foundation Ready | ⏳ Frontend Next
