// Base types
export interface Project {
  id: string
  name: string
  description?: string
  field_template_id?: string
  status: 'ACTIVE' | 'ARCHIVED'
  created_at: string
  updated_at: string
}

export interface ProjectDetail extends Project {
  document_count: number
  extracted_count: number
  pending_count: number
}

export interface Document {
  id: string
  project_id: string
  filename: string
  file_type: string
  file_size: number
  upload_status: 'UPLOADED' | 'PARSING' | 'PARSED' | 'FAILED'
  error_message?: string
  created_at: string
  updated_at: string
}

export interface DocumentDetail extends Document {
  parsed_text_preview?: string
  metadata?: Record<string, any>
  extraction_status?: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED'
}

export interface FieldDefinition {
  field_id: string
  field_name: string
  field_type: 'TEXT' | 'DATE' | 'NUMBER' | 'BOOLEAN' | 'LIST'
  required: boolean
  validation_rules?: Record<string, any>
  normalization?: string
  extraction_prompt?: string
}

export interface FieldTemplate {
  id: string
  name: string
  version: number
  fields: FieldDefinition[]
  created_at: string
  updated_at: string
}

export interface Citation {
  source: string
  text_snippet: string
}

export interface ExtractedField {
  field_id: string
  raw_value?: string
  normalized_value?: string
  confidence_score: number
  citations: Citation[]
}

export interface ExtractedRecord {
  id: string
  document_id: string
  field_template_id: string
  extraction_status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED'
  extracted_fields?: ExtractedField[]
  error_message?: string
  created_at: string
  updated_at: string
}

export interface ReviewRecord {
  id: string
  extracted_record_id: string
  field_id: string
  review_status: 'CONFIRMED' | 'REJECTED' | 'MANUAL_UPDATED' | 'MISSING_DATA' | 'PENDING'
  manual_value?: string
  reviewer_notes?: string
  reviewed_by?: string
  reviewed_at: string
}

export interface ReviewFieldData {
  field_name: string
  extracted_value?: string
  normalized_value?: string
  confidence_score: number
  review_status: string
  manual_value?: string
  final_value?: string
  citations: Citation[]
}

export interface ReviewTableRow {
  document_id: string
  document_name: string
  fields: Record<string, ReviewFieldData>
}

export interface ReviewTableResponse {
  columns: string[]
  rows: ReviewTableRow[]
}

export interface TaskStatus {
  task_id: string
  task_type: string
  status: string
  progress: number
  result?: any
  error?: string
}

// Request types
export interface CreateProjectRequest {
  name: string
  description?: string
  field_template_id?: string
}

export interface UpdateProjectRequest {
  name?: string
  description?: string
  field_template_id?: string
  status?: 'ACTIVE' | 'ARCHIVED'
}

export interface CreateFieldTemplateRequest {
  name: string
  fields: FieldDefinition[]
}

export interface CreateReviewRequest {
  extracted_record_id: string
  field_id: string
  review_status: 'CONFIRMED' | 'REJECTED' | 'MANUAL_UPDATED' | 'MISSING_DATA' | 'PENDING'
  manual_value?: string
  reviewer_notes?: string
}

export interface ExtractionRequest {
  field_template_id: string
  force_reprocess?: boolean
}

