'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter, useParams } from 'next/navigation'
import { api } from '@/lib/api-client'
import type { Document } from '@/types'
import { 
  ArrowLeftIcon, 
  UploadIcon, 
  FileTextIcon, 
  Trash2Icon, 
  DownloadIcon,
  PlayIcon,
  CheckCircle2Icon,
  XCircleIcon,
  LoaderIcon
} from 'lucide-react'

export default function ProjectDetailPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const projectId = params.id as string

  const [uploadingFiles, setUploadingFiles] = useState<File[]>([])
  const [isDragging, setIsDragging] = useState(false)

  // Fetch project details
  const { data: project, isLoading: projectLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => api.projects.get(projectId),
  })

  // Fetch documents
  const { data: documents, isLoading: docsLoading } = useQuery({
    queryKey: ['documents', projectId],
    queryFn: () => api.documents.list(projectId),
  })

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: ({ file }: { file: File }) => api.documents.upload(projectId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', projectId] })
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (documentId: string) => api.documents.delete(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', projectId] })
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  // Trigger extraction mutation
  const extractMutation = useMutation({
    mutationFn: () => api.extraction.triggerProject(projectId, false),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', projectId] })
    },
  })

  const handleFileSelect = async (files: FileList | null) => {
    if (!files) return

    const fileArray = Array.from(files)
    setUploadingFiles(fileArray)

    for (const file of fileArray) {
      try {
        await uploadMutation.mutateAsync({ file })
      } catch (error) {
        console.error('Upload failed:', error)
      }
    }

    setUploadingFiles([])
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    handleFileSelect(e.dataTransfer.files)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  if (projectLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Project Not Found</h2>
          <button
            onClick={() => router.push('/projects')}
            className="text-blue-600 hover:text-blue-800"
          >
            ← Back to Projects
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <button
            onClick={() => router.push('/projects')}
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-1" />
            Back to Projects
          </button>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
              {project.description && (
                <p className="mt-2 text-sm text-gray-600">{project.description}</p>
              )}
              
              {/* Stats */}
              <div className="mt-4 flex items-center space-x-6 text-sm">
                <div className="flex items-center">
                  <FileTextIcon className="h-4 w-4 text-gray-400 mr-1" />
                  <span className="text-gray-600">
                    {project.document_count || 0} documents
                  </span>
                </div>
                <div className="flex items-center">
                  <CheckCircle2Icon className="h-4 w-4 text-green-500 mr-1" />
                  <span className="text-gray-600">
                    {project.extracted_count || 0} extracted
                  </span>
                </div>
                <div className="flex items-center">
                  <LoaderIcon className="h-4 w-4 text-yellow-500 mr-1" />
                  <span className="text-gray-600">
                    {project.pending_count || 0} pending
                  </span>
                </div>
              </div>
            </div>

            <div className="flex space-x-3">
              {project.field_template_id && (
                <button
                  onClick={() => extractMutation.mutate()}
                  disabled={extractMutation.isPending}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <PlayIcon className="h-4 w-4 mr-2" />
                  {extractMutation.isPending ? 'Extracting...' : 'Extract All'}
                </button>
              )}
              <button
                onClick={() => router.push(`/projects/${projectId}/review`)}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Review Table →
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Area */}
        <div
          className={`mb-8 border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 bg-white hover:border-gray-400'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <UploadIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Upload documents</h3>
          <p className="mt-1 text-sm text-gray-500">
            Drag and drop files here, or click to browse
          </p>
          <p className="mt-1 text-xs text-gray-400">
            Supported: PDF, DOCX, HTML, TXT (Max 50MB)
          </p>
          <div className="mt-4">
            <label className="cursor-pointer inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
              <UploadIcon className="h-4 w-4 mr-2" />
              Select Files
              <input
                type="file"
                multiple
                accept=".pdf,.docx,.html,.htm,.txt"
                onChange={(e) => handleFileSelect(e.target.files)}
                className="hidden"
              />
            </label>
          </div>

          {uploadingFiles.length > 0 && (
            <div className="mt-4">
              <p className="text-sm text-gray-600">
                Uploading {uploadingFiles.length} file(s)...
              </p>
            </div>
          )}
        </div>

        {/* Documents List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Documents</h2>
          </div>

          {docsLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : documents && documents.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {documents.map((doc) => (
                <DocumentRow
                  key={doc.id}
                  document={doc}
                  onDelete={() => deleteMutation.mutate(doc.id)}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <FileTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No documents</h3>
              <p className="mt-1 text-sm text-gray-500">
                Upload documents to get started with extraction.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function DocumentRow({
  document,
  onDelete,
}: {
  document: Document
  onDelete: () => void
}) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      UPLOADED: 'bg-gray-100 text-gray-800',
      PARSING: 'bg-yellow-100 text-yellow-800',
      PARSED: 'bg-green-100 text-green-800',
      FAILED: 'bg-red-100 text-red-800',
    }

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status]}`}>
        {status === 'PARSING' && <LoaderIcon className="animate-spin h-3 w-3 mr-1" />}
        {status === 'PARSED' && <CheckCircle2Icon className="h-3 w-3 mr-1" />}
        {status === 'FAILED' && <XCircleIcon className="h-3 w-3 mr-1" />}
        {status}
      </span>
    )
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <>
      <div className="px-6 py-4 hover:bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center min-w-0 flex-1">
            <FileTextIcon className="h-8 w-8 text-blue-500 flex-shrink-0" />
            <div className="ml-4 min-w-0 flex-1">
              <div className="flex items-center space-x-2">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {document.filename}
                </p>
                {getStatusBadge(document.upload_status)}
              </div>
              <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                <span>{document.file_type.toUpperCase()}</span>
                <span>{formatFileSize(document.file_size)}</span>
                <span>{new Date(document.created_at).toLocaleDateString()}</span>
              </div>
              {document.error_message && (
                <p className="mt-1 text-sm text-red-600">{document.error_message}</p>
              )}
            </div>
          </div>

          <div className="ml-4 flex items-center space-x-2">
            <button
              onClick={() => api.documents.download(document.id)}
              className="p-2 text-gray-400 hover:text-gray-600"
              title="Download"
            >
              <DownloadIcon className="h-5 w-5" />
            </button>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="p-2 text-red-400 hover:text-red-600"
              title="Delete"
            >
              <Trash2Icon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-sm w-full mx-4">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900">Delete Document?</h3>
              <p className="mt-2 text-sm text-gray-500">
                Are you sure you want to delete "{document.filename}"?
              </p>
            </div>
            <div className="px-6 py-3 bg-gray-50 rounded-b-lg flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onDelete()
                  setShowDeleteConfirm(false)
                }}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
