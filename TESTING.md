# Testing Guide - Legal Tabular Review System

This document provides step-by-step instructions for testing the complete Legal Tabular Review system.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Starting the Application](#starting-the-application)
4. [Testing Workflow](#testing-workflow)
5. [API Testing](#api-testing)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before testing, ensure you have:
- Docker and Docker Compose installed
- Google Gemini API key (free tier available at https://ai.google.dev/)
- Ports available: 3004, 8004, 5436, 6383, 5559
- At least 4GB free RAM

---

## Environment Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/fahadhasan-x/Legal_Tebular_review.git
cd Legal_Tebular_review
```

### Step 2: Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file and add your API key
# Find this line: GEMINI_API_KEY=your-gemini-api-key-here
# Replace with: GEMINI_API_KEY=AIzaSy...your-actual-key
```

**Get your Gemini API key:**
1. Visit https://ai.google.dev/
2. Click "Get API Key"
3. Copy the key and paste it in `.env`

### Step 3: Verify Environment File
```bash
# Check that your .env file has the API key
grep "GEMINI_API_KEY" .env

# Expected output: GEMINI_API_KEY=AIzaSy...
```

---

## Starting the Application

### Step 1: Build and Start All Services
```bash
# Start all containers in detached mode
docker-compose up -d

# This will start:
# - PostgreSQL database (port 5436)
# - Redis cache (port 6383)
# - Backend API (port 8004)
# - Frontend app (port 3004)
# - Celery worker
# - Flower monitoring (port 5559)
```

### Step 2: Monitor Service Health
```bash
# Check if all containers are running
docker-compose ps

# Expected output: All services should show "Up" status
```

### Step 3: View Logs (if needed)
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery_worker
```

### Step 4: Wait for Services to Initialize
```bash
# Wait 30-60 seconds for all services to be ready
# Backend should show: "Application startup complete"
# Frontend should show: "Ready in X ms"
```

---

## Testing Workflow

### Test 1: Frontend Access
**Objective:** Verify the frontend is accessible

1. Open browser and navigate to: http://localhost:3004
2. You should see the Legal Tabular Review homepage
3. Check for navigation menu (Upload, Review, Export)

**Expected Result:** ✅ Frontend loads without errors

---

### Test 2: Backend API Access
**Objective:** Verify the backend API is running

1. Navigate to: http://localhost:8004/docs
2. You should see the FastAPI Swagger documentation
3. Look for sections: Documents, Extraction, Review

**Expected Result:** ✅ API documentation page loads with all endpoints listed

---

### Test 3: Upload a Legal Document
**Objective:** Test document upload and parsing

#### Using the Frontend:
1. Go to: http://localhost:3004/upload
2. Click "Choose File" or drag-and-drop a document
3. Select a sample document from the `data/` folder:
   - `Supply Agreement.pdf`
   - `tsla-ex102_486.htm.pdf`
   - `EX-10.2.html`

4. Click "Upload Document"

**Expected Result:** 
- ✅ Progress bar shows upload status
- ✅ Success message appears
- ✅ Document ID is displayed

#### Using the API (Alternative):
```bash
# Upload via API
curl -X POST "http://localhost:8004/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/Supply Agreement.pdf"
```

**Expected Response:**
```json
{
  "id": "uuid-here",
  "filename": "Supply Agreement.pdf",
  "status": "uploaded",
  "created_at": "2026-02-06T..."
}
```

---

### Test 4: AI Field Extraction
**Objective:** Test automatic field extraction using Gemini AI

#### Using the Frontend:
1. After uploading, you'll see an "Extract Fields" button
2. Click "Extract Fields"
3. A background task will start (you can monitor at http://localhost:5559 - Flower dashboard)

#### Using the API:
```bash
# Start extraction (replace {document_id} with actual ID from upload)
curl -X POST "http://localhost:8004/api/v1/extraction/extract/{document_id}"
```

**Expected Result:**
- ✅ Task ID is returned
- ✅ Status shows "processing"
- ✅ After 30-60 seconds, status changes to "completed"

#### Monitor Task Progress:
1. Go to Flower dashboard: http://localhost:5559
2. Look for your task in the "Tasks" tab
3. Status should progress: PENDING → STARTED → SUCCESS

---

### Test 5: View Extracted Fields
**Objective:** Verify extracted fields are displayed correctly

#### Using the Frontend:
1. Navigate to: http://localhost:3004/review
2. Select the document you uploaded
3. View the extracted fields table

**Expected Fields:**
- Party Names
- Effective Date
- Contract Value/Amount
- Payment Terms
- Termination Clause
- Governing Law
- Key Obligations
- Deliverables

**Check for:**
- ✅ Field Name
- ✅ Extracted Value
- ✅ Confidence Score (0-100%)
- ✅ Citation/Page Reference
- ✅ Color coding (Green: High confidence, Yellow: Medium, Red: Low)

#### Using the API:
```bash
# Get extraction results
curl "http://localhost:8004/api/v1/extraction/{document_id}/results"
```

**Expected Response:**
```json
{
  "document_id": "uuid",
  "status": "completed",
  "fields": [
    {
      "field_name": "party_names",
      "value": "Tesla, Inc. and Panasonic Corporation",
      "confidence": 95.5,
      "citation": "Page 1, Section 1"
    },
    ...
  ]
}
```

---

### Test 6: Human Review & Editing
**Objective:** Test the review workflow with inline editing

1. In the Review page (http://localhost:3004/review)
2. Click "Edit" button next to any field
3. Modify the value
4. Click "Save"

**Expected Result:**
- ✅ Edit mode activates
- ✅ Value changes are saved
- ✅ Confidence score updates to 100% (manual review)
- ✅ "Reviewed by Human" badge appears

#### Using the API:
```bash
# Update a field
curl -X PUT "http://localhost:8004/api/v1/review/fields/{field_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "value": "Updated value",
    "reviewed_by": "Tester",
    "notes": "Manual correction"
  }'
```

---

### Test 7: Multi-Document Comparison
**Objective:** Test side-by-side comparison of multiple documents

1. Upload 2-3 different documents (use samples from `data/` folder)
2. Extract fields from all documents
3. Navigate to: http://localhost:3004/review?view=comparison
4. Select multiple documents from the dropdown

**Expected Result:**
- ✅ Table shows documents side-by-side
- ✅ Same fields are aligned horizontally
- ✅ Values from different documents are comparable
- ✅ Differences are highlighted

**Example Table:**
| Field | Document 1 | Document 2 | Document 3 |
|-------|------------|------------|------------|
| Party Names | Tesla & Panasonic | Tesla & LG | Tesla & CATL |
| Amount | $5B | $2.5B | $10B |
| Term | 10 years | 5 years | 7 years |

---

### Test 8: Export Functionality
**Objective:** Test data export to CSV/Excel

#### Using the Frontend:
1. In Review page, click "Export" button
2. Select format: CSV or Excel
3. Click "Download"

**Expected Result:**
- ✅ File downloads automatically
- ✅ File contains all fields and values
- ✅ Includes confidence scores and citations
- ✅ Opens correctly in Excel/Google Sheets

#### Using the API:
```bash
# Export to CSV
curl "http://localhost:8004/api/v1/export/{document_id}/csv" -o output.csv

# Export to Excel
curl "http://localhost:8004/api/v1/export/{document_id}/excel" -o output.xlsx
```

**Verify Export File:**
```bash
# Check CSV content
head -5 output.csv

# Expected columns:
# field_name,value,confidence,citation,reviewed
```

---

### Test 9: Confidence-Based Filtering
**Objective:** Test filtering by confidence scores

1. In Review page, use the confidence filter slider
2. Set minimum confidence to 80%
3. Only fields with ≥80% confidence should display

**API Test:**
```bash
# Get high-confidence fields only
curl "http://localhost:8004/api/v1/extraction/{document_id}/results?min_confidence=80"
```

**Expected Result:**
- ✅ Low-confidence fields are hidden
- ✅ Counter shows number of filtered fields
- ✅ Can toggle between "All" and "High Confidence"

---

### Test 10: Background Task Monitoring
**Objective:** Monitor async task processing

1. Open Flower dashboard: http://localhost:5559
2. Upload a large document (PDF with 50+ pages)
3. Start extraction
4. Watch the task in Flower

**Expected Result:**
- ✅ Task appears in "Active" section
- ✅ Progress updates in real-time
- ✅ Task moves to "Completed" when done
- ✅ Execution time is logged

---

## API Testing

### Health Check Endpoints

```bash
# Backend health
curl http://localhost:8004/health
# Expected: {"status": "healthy"}

# Database connection
curl http://localhost:8004/api/v1/health/db
# Expected: {"database": "connected"}

# Redis connection
curl http://localhost:8004/api/v1/health/redis
# Expected: {"redis": "connected"}
```

---

### Complete API Testing Flow

```bash
# 1. Upload document
UPLOAD_RESPONSE=$(curl -X POST "http://localhost:8004/api/v1/documents/upload" \
  -F "file=@data/Supply Agreement.pdf")

# Extract document ID
DOC_ID=$(echo $UPLOAD_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)

echo "Document ID: $DOC_ID"

# 2. Start extraction
curl -X POST "http://localhost:8004/api/v1/extraction/extract/$DOC_ID"

# 3. Wait 30 seconds
sleep 30

# 4. Get results
curl "http://localhost:8004/api/v1/extraction/$DOC_ID/results"

# 5. Get specific field
curl "http://localhost:8004/api/v1/extraction/$DOC_ID/results?field=party_names"

# 6. Export to CSV
curl "http://localhost:8004/api/v1/export/$DOC_ID/csv" -o test_export.csv

echo "Testing complete! Check test_export.csv"
```

---

## Troubleshooting

### Issue: Services won't start

**Solution:**
```bash
# Check port conflicts
netstat -ano | findstr "3004 8004 5436 6383 5559"

# Stop all containers
docker-compose down

# Remove volumes and restart
docker-compose down -v
docker-compose up -d
```

---

### Issue: API returns 500 errors

**Check logs:**
```bash
docker-compose logs backend | tail -50
```

**Common causes:**
- Missing Gemini API key in `.env`
- Database not initialized
- Redis not connected

**Solution:**
```bash
# Verify environment variables
docker-compose exec backend env | grep GEMINI_API_KEY

# Restart backend
docker-compose restart backend
```

---

### Issue: Frontend shows connection errors

**Check backend status:**
```bash
# Test backend directly
curl http://localhost:8004/health

# If backend is down, restart:
docker-compose restart backend
docker-compose restart frontend
```

---

### Issue: Extraction takes too long or fails

**Causes:**
- Large document (100+ pages)
- Gemini API rate limit (1500 requests/day on free tier)
- Network connectivity issues

**Check Flower dashboard:**
1. Go to http://localhost:5559
2. Look for failed tasks
3. Check error messages

**View Celery logs:**
```bash
docker-compose logs celery_worker | tail -100
```

---

### Issue: Low confidence scores

**This is expected for:**
- Scanned PDFs (OCR quality)
- Handwritten documents
- Complex legal language
- Unusual formatting

**Solutions:**
- Use higher quality document scans
- Enable OCR preprocessing (if available)
- Manually review and correct low-confidence fields

---

## Performance Testing

### Load Testing (Optional)

Test with multiple concurrent uploads:

```bash
# Upload 5 documents simultaneously
for i in {1..5}; do
  curl -X POST "http://localhost:8004/api/v1/documents/upload" \
    -F "file=@data/Supply Agreement.pdf" &
done

# Monitor Celery worker
docker-compose logs -f celery_worker
```

**Expected behavior:**
- All uploads succeed
- Tasks are queued and processed sequentially
- No memory leaks or crashes

---

## Test Completion Checklist

- [ ] Frontend loads at http://localhost:3004
- [ ] Backend API docs load at http://localhost:8004/docs
- [ ] Document upload succeeds
- [ ] Field extraction completes successfully
- [ ] Extracted fields display with confidence scores
- [ ] Manual editing and review works
- [ ] Multi-document comparison displays correctly
- [ ] Export to CSV/Excel works
- [ ] Confidence filtering works
- [ ] Flower dashboard accessible at http://localhost:5559
- [ ] All health check endpoints return success
- [ ] No errors in docker-compose logs

---

## Sample Test Data

The repository includes these sample documents in the `data/` folder:

1. **Supply Agreement.pdf** - Standard supply contract
2. **tsla-ex102_486.htm.pdf** - Tesla SEC filing exhibit
3. **tsla-ex103_198.htm.pdf** - Tesla manufacturing agreement
4. **EX-10.2.html** - HTML format legal document

All documents contain typical legal fields suitable for testing the extraction system.

---

## Expected Test Results

After completing all tests, you should have:

1. ✅ **3-4 uploaded documents** in the system
2. ✅ **Extracted fields** from each document with confidence scores
3. ✅ **Comparison table** showing side-by-side field values
4. ✅ **Exported CSV/Excel files** with all data
5. ✅ **Reviewed and edited fields** marked as human-verified
6. ✅ **Clean logs** with no critical errors

---

## Next Steps After Testing

1. Review the extracted fields for accuracy
2. Test with your own legal documents
3. Customize field templates in `backend/app/templates/legal_fields.py`
4. Adjust confidence thresholds in settings
5. Set up production deployment (see `DEPLOYMENT.md`)

---

## Support

If you encounter issues during testing:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review logs: `docker-compose logs -f`
3. Verify environment variables in `.env`
4. Ensure all ports are available
5. Restart services: `docker-compose restart`

For additional help, see:
- `README.md` - General overview
- `QUICKSTART.md` - Quick setup guide
- `TECH_STACK.md` - Technical details

---

**Happy Testing! 🚀**
