import Link from 'next/link'
import { FileText, Plus } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <FileText className="h-16 w-16 text-blue-600" />
          </div>
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Legal Tabular Review
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            AI-powered legal document extraction and comparison system
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-blue-600 mb-4">
              <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Document Upload</h3>
            <p className="text-gray-600">
              Support for PDF, DOCX, HTML, and TXT formats
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-blue-600 mb-4">
              <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">AI Extraction</h3>
            <p className="text-gray-600">
              Powered by Google Gemini with confidence scores
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-blue-600 mb-4">
              <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Review Table</h3>
            <p className="text-gray-600">
              Side-by-side comparison with manual review
            </p>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <Link
            href="/projects"
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-lg"
          >
            <Plus className="h-5 w-5" />
            Get Started
          </Link>
        </div>

        {/* Stats */}
        <div className="mt-16 grid md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold text-blue-600">85%+</div>
            <div className="text-gray-600 mt-2">Extraction Accuracy</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-blue-600">FREE</div>
            <div className="text-gray-600 mt-2">Gemini API Tier</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-blue-600">4</div>
            <div className="text-gray-600 mt-2">File Formats</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-blue-600">∞</div>
            <div className="text-gray-600 mt-2">Projects</div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-16 text-center text-gray-500 text-sm">
          <p>Powered by FastAPI, Next.js, and Google Gemini</p>
          <p className="mt-2">
            <a href="http://localhost:8004/docs" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
              API Documentation
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
