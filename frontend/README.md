# Legal Tabular Review - Frontend

**Next.js 14 Frontend for AI-Powered Legal Document Review**

---

## 🎯 Overview

This is the **frontend user interface** for the Legal Tabular Review system. Built with Next.js 14, TypeScript, and Tailwind CSS, it provides an intuitive experience for document upload, AI extraction review, and side-by-side comparison.

**Key Features:**
- 🎨 Modern, responsive UI with Tailwind CSS
- 📤 Drag & drop file upload
- 📊 Interactive review table (side-by-side comparison)
- ✅ Inline editing with confidence scores
- 📍 Citation viewer
- ⚡ Real-time status updates (auto-refresh)
- 🎯 Color-coded confidence indicators

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              Next.js 14 App Router              │
│  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │ Home    │→ │Projects │→ │ Project Detail  │ │
│  │ Page    │  │ List    │  │ + Upload        │ │
│  └─────────┘  └─────────┘  └─────────────────┘ │
│                                      ↓          │
│                             ┌─────────────────┐ │
│                             │ Review Table    │ │
│                             │ (Main Feature)  │ │
│                             └─────────────────┘ │
└─────────────────────────────────────────────────┘
                    ↓
         ┌──────────────────────┐
         │   FastAPI Backend    │
         │   (REST API)         │
         └──────────────────────┘
```

---

## 📂 Project Structure

```
frontend/
├── src/
│   ├── app/                       # Next.js App Router
│   │   ├── layout.tsx             # Root layout
│   │   ├── page.tsx               # Home page (104 lines)
│   │   ├── providers.tsx          # React Query provider
│   │   ├── globals.css            # Global styles
│   │   │
│   │   └── projects/
│   │       ├── page.tsx           # Projects list (350 lines)
│   │       └── [id]/
│   │           ├── page.tsx       # Project detail + upload (350 lines)
│   │           └── review/
│   │               └── page.tsx   # Review table ⭐ (400 lines)
│   │
│   ├── lib/
│   │   ├── api-client.ts          # API client (180 lines)
│   │   └── utils.ts               # Utility functions
│   │
│   └── types/
│       └── index.ts               # TypeScript types (140 lines)
│
├── public/                        # Static assets
│
├── next.config.js                 # Next.js configuration
├── tailwind.config.js             # Tailwind CSS config
├── tsconfig.json                  # TypeScript config
├── package.json                   # Dependencies
├── Dockerfile                     # Docker image
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# From project root
cd legal-tabular-review

# Start frontend + backend
docker-compose up frontend backend

# Frontend runs at http://localhost:3004
```

### Option 2: Local Development

```bash
cd frontend

# Install dependencies
npm install

# Set environment variable
export NEXT_PUBLIC_API_URL=http://localhost:8004/api/v1

# Start dev server
npm run dev  # http://localhost:3000

# Build for production
npm run build
npm start
```

---

## 📄 Pages

### **Home Page** (`app/page.tsx`)
- Hero section with project overview
- Feature cards (Upload, AI Extraction, Review Table)
- Call-to-action button
- Project stats

### **Projects List** (`app/projects/page.tsx`)
- Grid of project cards
- Each card shows:
  - Project name
  - Document count
  - Extraction status
  - Last updated
- Create new project modal
- Delete project with confirmation

### **Project Detail** (`app/projects/[id]/page.tsx`)
- **Drag & drop file uploader** ⭐
- Document list with status badges:
  - 🔵 UPLOADED
  - 🟡 PARSING
  - 🟢 PARSED
  - 🔴 FAILED
- Upload progress tracking
- Download documents
- Delete documents
- "Extract All" button
- "Review Table" navigation

### **Review Table** (`app/projects/[id]/review/page.tsx`) ⭐⭐⭐

**Main feature of the system:**

- **Side-by-side comparison table:**
  - Rows = Documents
  - Columns = Extracted fields
  - Cells = Values + confidence + citations

- **Interactive features:**
  - Click cell to edit
  - Save/cancel buttons
  - Review actions (Confirm/Reject)
  - Show/hide citations

- **Visual indicators:**
  - 🟢 Green (>0.9) - High confidence
  - 🟡 Yellow (0.7-0.9) - Medium confidence
  - 🔴 Red (<0.7) - Low confidence

- **Auto-refresh:** Every 5 seconds
- **Sticky headers:** For easy navigation
- **Horizontal scroll:** For many fields

---

## 📦 Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript 5
- **Styling:** Tailwind CSS 3.4
- **Components:** shadcn/ui (Radix UI primitives)
- **State Management:** TanStack Query (React Query) + Zustand
- **HTTP Client:** Axios
- **Forms:** react-hook-form + zod
- **Icons:** Lucide React

---

## 🎨 UI Components

### **Custom Components**

- `FileUploader` - Drag & drop file upload
- `ReviewTable` - Side-by-side comparison table
- `ReviewCell` - Individual field cell with actions
- `StatusBadge` - Color-coded status indicator
- `ConfidenceBar` - Visual confidence meter
- `CitationPopover` - Citation viewer

### **shadcn/ui Components**

- `Button`, `Card`, `Dialog`, `Popover`
- `Select`, `Input`, `Label`
- `Toast`, `Badge`

---

## 🔄 API Integration

All API calls are centralized in `lib/api-client.ts`:

```typescript
import { apiClient } from '@/lib/api-client'

// Get projects
const projects = await apiClient.getProjects()

// Upload document
const document = await apiClient.uploadDocument(projectId, file)

// Get review table data
const reviewTable = await apiClient.getReviewTable(projectId)

// Update review
await apiClient.createReview({
  extracted_record_id: recordId,
  field_id: 'parties',
  review_status: 'CONFIRMED'
})
```

---

## 🧪 Testing

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage

# E2E tests (future)
npm run test:e2e
```

---

## 🎯 Development Workflow

### Start Development Server

```bash
npm run dev  # http://localhost:3000
```

### Lint & Format

```bash
# ESLint
npm run lint

# Fix linting issues
npm run lint -- --fix

# Format with Prettier (if configured)
npm run format
```

### Build for Production

```bash
# Build
npm run build

# Test production build locally
npm start
```

---

## 🔧 Configuration

### Environment Variables

Create `.env.local` file:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8004/api/v1
```

### Tailwind Configuration

See `tailwind.config.js` for custom theme settings:
- Colors
- Fonts
- Breakpoints
- Spacing

---

## 📊 Key Features Explained

### **1. File Upload**

Uses drag & drop with `react-dropzone`:

```typescript
const onDrop = (acceptedFiles: File[]) => {
  acceptedFiles.forEach(file => {
    uploadDocument.mutate({ projectId, file })
  })
}
```

### **2. Review Table**

Dynamic table with inline editing:

```typescript
const ReviewTable = ({ projectId }) => {
  const { data } = useQuery({
    queryKey: ['review-table', projectId],
    queryFn: () => apiClient.getReviewTable(projectId),
    refetchInterval: 5000  // Auto-refresh
  })
  
  return (
    <table>
      <thead>
        <tr>
          <th>Document</th>
          {data?.columns.map(col => <th key={col}>{col}</th>)}
        </tr>
      </thead>
      <tbody>
        {data?.rows.map(row => (
          <ReviewRow key={row.document_id} row={row} />
        ))}
      </tbody>
    </table>
  )
}
```

### **3. Confidence Color Coding**

```typescript
const getConfidenceColor = (score: number) => {
  if (score >= 0.9) return 'bg-green-100 text-green-800'
  if (score >= 0.7) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
}
```

---

## 🐛 Troubleshooting

### Issue: API connection failed
**Solution:** Check `NEXT_PUBLIC_API_URL` in `.env.local` and ensure backend is running

### Issue: Tailwind styles not working
**Solution:** Run `npm install` and restart dev server

### Issue: Type errors
**Solution:** Run `npm run type-check` and fix reported issues

---

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Run linter: `npm run lint`
4. Test locally: `npm run dev`
5. Commit: `git commit -m 'feat: add amazing feature'`
6. Push: `git push origin feature/amazing-feature`

---

## 📄 License

MIT License

---

## 👤 Maintainer

**Fahad Hasan**
- Email: fahad.hasan.42931@gmail.com

---

**Built with Next.js 14 + TypeScript + Tailwind CSS 🚀**
