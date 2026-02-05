import axios from 'axios'
import type {
  Project,
  ProjectDetail,
  CreateProjectRequest,
  UpdateProjectRequest,
  Document,
  DocumentDetail,
  FieldTemplate,
  CreateFieldTemplateRequest,
  ExtractedRecord,
  ReviewRecord,
  ReviewTableResponse,
  CreateReviewRequest,
  ExtractionRequest,
  TaskStatus,
} from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8004/api/v1'

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token here in future
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle errors globally
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// API functions
export const api = {
  // Projects
  projects: {
    list: async (params?: { skip?: number; limit?: number }) => {
      const response = await apiClient.get<Project[]>('/projects', { params })
      return response.data
    },
    get: async (id: string) => {
      const response = await apiClient.get<ProjectDetail>(`/projects/${id}`)
      return response.data
    },
    create: async (data: CreateProjectRequest) => {
      const response = await apiClient.post<Project>('/projects', data)
      return response.data
    },
    update: async (id: string, data: UpdateProjectRequest) => {
      const response = await apiClient.put<Project>(`/projects/${id}`, data)
      return response.data
    },
    delete: async (id: string) => {
      await apiClient.delete(`/projects/${id}`)
    },
  },

  // Documents
  documents: {
    list: async (projectId: string, params?: { skip?: number; limit?: number }) => {
      const response = await apiClient.get<Document[]>(`/projects/${projectId}/documents`, { params })
      return response.data
    },
    get: async (documentId: string) => {
      const response = await apiClient.get<DocumentDetail>(`/documents/${documentId}`)
      return response.data
    },
    upload: async (projectId: string, file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const response = await apiClient.post<Document>(
        `/projects/${projectId}/documents/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )
      return response.data
    },
    delete: async (documentId: string) => {
      await apiClient.delete(`/documents/${documentId}`)
    },
    download: async (documentId: string) => {
      const response = await apiClient.get(`/documents/${documentId}/download`, {
        responseType: 'blob',
      })
      return response.data
    },
  },

  // Field Templates
  fieldTemplates: {
    list: async (params?: { skip?: number; limit?: number }) => {
      const response = await apiClient.get<FieldTemplate[]>('/field-templates', { params })
      return response.data
    },
    get: async (id: string) => {
      const response = await apiClient.get<FieldTemplate>(`/field-templates/${id}`)
      return response.data
    },
    create: async (data: CreateFieldTemplateRequest) => {
      const response = await apiClient.post<FieldTemplate>('/field-templates', data)
      return response.data
    },
    update: async (id: string, data: Partial<CreateFieldTemplateRequest>, triggerReExtraction = false) => {
      const response = await apiClient.put<FieldTemplate>(
        `/field-templates/${id}`,
        data,
        { params: { trigger_re_extraction: triggerReExtraction } }
      )
      return response.data
    },
    delete: async (id: string) => {
      await apiClient.delete(`/field-templates/${id}`)
    },
  },

  // Extraction
  extraction: {
    trigger: async (documentId: string, data: ExtractionRequest) => {
      const response = await apiClient.post<TaskStatus>(`/documents/${documentId}/extract`, data)
      return response.data
    },
    triggerProject: async (projectId: string, forceReprocess = false) => {
      const response = await apiClient.post<TaskStatus>(
        `/projects/${projectId}/extract-all`,
        {},
        { params: { force_reprocess: forceReprocess } }
      )
      return response.data
    },
    getDocumentExtractions: async (documentId: string) => {
      const response = await apiClient.get<ExtractedRecord[]>(`/documents/${documentId}/extractions`)
      return response.data
    },
    getRecord: async (recordId: string) => {
      const response = await apiClient.get<ExtractedRecord>(`/extractions/${recordId}`)
      return response.data
    },
  },

  // Review
  review: {
    create: async (data: CreateReviewRequest) => {
      const response = await apiClient.post<ReviewRecord>('/reviews', data)
      return response.data
    },
    bulkCreate: async (data: CreateReviewRequest[]) => {
      const response = await apiClient.post('/reviews/bulk', data)
      return response.data
    },
    getExtractionReviews: async (extractedRecordId: string) => {
      const response = await apiClient.get<ReviewRecord[]>(`/extractions/${extractedRecordId}/reviews`)
      return response.data
    },
    getProjectReviewTable: async (projectId: string) => {
      const response = await apiClient.get<ReviewTableResponse>(`/projects/${projectId}/review-table`)
      return response.data
    },
  },

  // Health check
  health: async () => {
    const response = await apiClient.get('/health', { baseURL: 'http://localhost:8004' })
    return response.data
  },
}

