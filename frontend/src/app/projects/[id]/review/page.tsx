'use client'

import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter, useParams } from 'next/navigation'
import { api } from '@/lib/api-client'
import type { ReviewTableResponse, ReviewFieldData, CreateReviewRequest } from '@/types'
import { 
  ArrowLeftIcon, 
  CheckCircle2Icon, 
  XCircleIcon,
  AlertCircleIcon,
  EditIcon,
  SaveIcon,
  XIcon
} from 'lucide-react'

export default function ReviewTablePage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const projectId = params.id as string

  const [editingCell, setEditingCell] = useState<{ docId: string; fieldId: string } | null>(null)
  const [editValue, setEditValue] = useState('')

  // Fetch review table
  const { data: reviewData, isLoading } = useQuery({
    queryKey: ['review-table', projectId],
    queryFn: () => api.review.getProjectReviewTable(projectId),
    refetchInterval: 5000, // Auto-refresh every 5 seconds
  })

  // Fetch project
  const { data: project } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => api.projects.get(projectId),
  })

  // Review mutation
  const reviewMutation = useMutation({
    mutationFn: (data: CreateReviewRequest) => api.review.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['review-table', projectId] })
      setEditingCell(null)
      setEditValue('')
    },
  })

  const handleCellEdit = useCallback((docId: string, fieldId: string, currentValue: string) => {
    setEditingCell({ docId, fieldId })
    setEditValue(currentValue || '')
  }, [])

  const handleSaveEdit = useCallback(async (
    docId: string,
    fieldId: string,
    extractedRecordId: string
  ) => {
    await reviewMutation.mutateAsync({
      extracted_record_id: extractedRecordId,
      field_id: fieldId,
      review_status: 'MANUAL_UPDATED',
      manual_value: editValue,
    })
  }, [editValue, reviewMutation])

  const handleConfirm = useCallback(async (
    extractedRecordId: string,
    fieldId: string
  ) => {
    await reviewMutation.mutateAsync({
      extracted_record_id: extractedRecordId,
      field_id: fieldId,
      review_status: 'CONFIRMED',
    })
  }, [reviewMutation])

  const handleReject = useCallback(async (
    extractedRecordId: string,
    fieldId: string
  ) => {
    await reviewMutation.mutateAsync({
      extracted_record_id: extractedRecordId,
      field_id: fieldId,
      review_status: 'REJECTED',
    })
  }, [reviewMutation])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!reviewData) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Review Data</h2>
          <button
            onClick={() => router.push(`/projects/${projectId}`)}
            className="text-blue-600 hover:text-blue-800"
          >
            ← Back to Project
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-full px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={() => router.push(`/projects/${projectId}`)}
                className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
              >
                <ArrowLeftIcon className="h-4 w-4 mr-1" />
                Back
              </button>
              <div className="ml-4">
                <h1 className="text-2xl font-bold text-gray-900">
                  {project?.name || 'Review Table'}
                </h1>
                <p className="text-sm text-gray-600">
                  {reviewData.rows.length} documents × {reviewData.columns.length} fields
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm">
                <div className="flex items-center">
                  <CheckCircle2Icon className="h-4 w-4 text-green-500 mr-1" />
                  <span>Confirmed</span>
                </div>
                <div className="flex items-center">
                  <AlertCircleIcon className="h-4 w-4 text-yellow-500 mr-1" />
                  <span>Pending</span>
                </div>
                <div className="flex items-center">
                  <XCircleIcon className="h-4 w-4 text-red-500 mr-1" />
                  <span>Rejected</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="p-4">
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50 sticky top-0">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50 z-10">
                    Document
                  </th>
                  {reviewData.columns.map((column) => (
                    <th
                      key={column}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[200px]"
                    >
                      {column}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {reviewData.rows.map((row) => (
                  <tr key={row.document_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white">
                      <div className="max-w-xs truncate" title={row.document_name}>
                        {row.document_name}
                      </div>
                    </td>
                    {Object.entries(row.fields).map(([fieldId, fieldData]) => (
                      <td
                        key={fieldId}
                        className="px-6 py-4 text-sm text-gray-900"
                      >
                        <ReviewCell
                          documentId={row.document_id}
                          fieldId={fieldId}
                          fieldData={fieldData}
                          isEditing={
                            editingCell?.docId === row.document_id &&
                            editingCell?.fieldId === fieldId
                          }
                          editValue={editValue}
                          onEdit={handleCellEdit}
                          onSave={handleSaveEdit}
                          onCancel={() => setEditingCell(null)}
                          onConfirm={handleConfirm}
                          onReject={handleReject}
                          onEditValueChange={setEditValue}
                        />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

function ReviewCell({
  documentId,
  fieldId,
  fieldData,
  isEditing,
  editValue,
  onEdit,
  onSave,
  onCancel,
  onConfirm,
  onReject,
  onEditValueChange,
}: {
  documentId: string
  fieldId: string
  fieldData: ReviewFieldData
  isEditing: boolean
  editValue: string
  onEdit: (docId: string, fieldId: string, currentValue: string) => void
  onSave: (docId: string, fieldId: string, extractedRecordId: string) => void
  onCancel: () => void
  onConfirm: (extractedRecordId: string, fieldId: string) => void
  onReject: (extractedRecordId: string, fieldId: string) => void
  onEditValueChange: (value: string) => void
}) {
  const [showCitations, setShowCitations] = useState(false)

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'CONFIRMED':
        return <CheckCircle2Icon className="h-4 w-4 text-green-500" />
      case 'REJECTED':
        return <XCircleIcon className="h-4 w-4 text-red-500" />
      case 'MANUAL_UPDATED':
        return <EditIcon className="h-4 w-4 text-blue-500" />
      case 'MISSING_DATA':
        return <AlertCircleIcon className="h-4 w-4 text-gray-400" />
      default:
        return <AlertCircleIcon className="h-4 w-4 text-yellow-500" />
    }
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600'
    if (score >= 0.5) return 'text-yellow-600'
    return 'text-red-600'
  }

  // Mock extracted record ID - in real app, this would come from the API
  const extractedRecordId = `${documentId}-record`

  if (isEditing) {
    return (
      <div className="space-y-2">
        <input
          type="text"
          value={editValue}
          onChange={(e) => onEditValueChange(e.target.value)}
          className="w-full px-2 py-1 border border-blue-500 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          autoFocus
        />
        <div className="flex space-x-2">
          <button
            onClick={() => onSave(documentId, fieldId, extractedRecordId)}
            className="inline-flex items-center px-2 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700"
          >
            <SaveIcon className="h-3 w-3 mr-1" />
            Save
          </button>
          <button
            onClick={onCancel}
            className="inline-flex items-center px-2 py-1 bg-gray-200 text-gray-700 rounded text-xs hover:bg-gray-300"
          >
            <XIcon className="h-3 w-3 mr-1" />
            Cancel
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            {getStatusIcon(fieldData.review_status)}
            <span className="font-medium">
              {fieldData.final_value || fieldData.normalized_value || fieldData.extracted_value || (
                <span className="text-gray-400 italic">No value</span>
              )}
            </span>
          </div>
          
          {fieldData.confidence_score > 0 && (
            <div className="mt-1">
              <span className={`text-xs ${getConfidenceColor(fieldData.confidence_score)}`}>
                Confidence: {(fieldData.confidence_score * 100).toFixed(0)}%
              </span>
            </div>
          )}

          {fieldData.manual_value && (
            <div className="mt-1 text-xs text-gray-500">
              Original: {fieldData.extracted_value}
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => onEdit(documentId, fieldId, fieldData.final_value || '')}
          className="text-xs text-blue-600 hover:text-blue-800"
        >
          Edit
        </button>
        {fieldData.review_status === 'PENDING' && fieldData.extracted_value && (
          <>
            <button
              onClick={() => onConfirm(extractedRecordId, fieldId)}
              className="text-xs text-green-600 hover:text-green-800"
            >
              Confirm
            </button>
            <button
              onClick={() => onReject(extractedRecordId, fieldId)}
              className="text-xs text-red-600 hover:text-red-800"
            >
              Reject
            </button>
          </>
        )}
        {fieldData.citations.length > 0 && (
          <button
            onClick={() => setShowCitations(!showCitations)}
            className="text-xs text-gray-600 hover:text-gray-800"
          >
            {showCitations ? 'Hide' : 'Show'} Source
          </button>
        )}
      </div>

      {/* Citations */}
      {showCitations && fieldData.citations.length > 0 && (
        <div className="mt-2 p-2 bg-gray-50 rounded border border-gray-200 text-xs">
          {fieldData.citations.map((citation, idx) => (
            <div key={idx} className="mb-2 last:mb-0">
              <div className="font-medium text-gray-700">{citation.source}</div>
              <div className="text-gray-600 italic">"{citation.text_snippet}"</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
