'use client';

import React, { useState } from 'react';
import { Upload, FileText, X, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { govDocumentsApi } from '@/lib/api';
import toast from 'react-hot-toast';
import Chatbot from './Chatbot';

interface GovEasyUploadProps {
  onDocumentUploaded?: (documentId: string) => void;
}

export default function GovEasyUpload({ onDocumentUploaded }: GovEasyUploadProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedDocumentId, setUploadedDocumentId] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileSelect = async (file: File) => {
    // Validate file type
    const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
      toast.error('Please upload a PDF or image file (PNG, JPG)');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size must be less than 10MB');
      return;
    }

    setUploading(true);
    try {
      const result = await govDocumentsApi.upload(file);
      setUploadedDocumentId(result.document_id);
      toast.success(`Document uploaded! ${result.extraction_status === 'success' ? 'Text extracted successfully.' : 'Extraction in progress...'}`);
      
      if (onDocumentUploaded) {
        onDocumentUploaded(result.document_id);
      }
    } catch (error: any) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(false);
    
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = () => {
    setDragActive(false);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-24 right-6 z-50 bg-gradient-to-br from-green-600 to-emerald-700 hover:from-green-700 hover:to-emerald-800 text-white rounded-full p-4 shadow-xl transition-all duration-300 hover:scale-110 hover:shadow-2xl"
          aria-label="Upload Government Document (GovEasy)"
          title="Upload Government Document"
        >
          <FileText className="w-6 h-6" />
        </button>
      )}

      {/* Upload Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={() => setIsOpen(false)}>
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="bg-gradient-to-r from-green-600 to-emerald-700 text-white px-6 py-4 flex items-center justify-between rounded-t-2xl">
              <div>
                <h2 className="text-xl font-bold">GovEasy - Upload Government Document</h2>
                <p className="text-sm text-green-100 mt-1">Upload circulars, letters, schemes for simple explanations</p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="w-8 h-8 flex items-center justify-center hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              {/* Upload Area */}
              {!uploadedDocumentId && (
                <div
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${
                    dragActive
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-300 bg-gray-50 hover:border-green-400 hover:bg-green-50/50'
                  } ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
                >
                  {uploading ? (
                    <div className="space-y-4">
                      <Loader2 className="w-12 h-12 text-green-600 animate-spin mx-auto" />
                      <p className="text-gray-600">Uploading and extracting text...</p>
                    </div>
                  ) : (
                    <>
                      <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-semibold text-gray-800 mb-2">
                        Drop your document here
                      </h3>
                      <p className="text-sm text-gray-500 mb-4">
                        Or click to browse
                      </p>
                      <input
                        type="file"
                        accept=".pdf,.png,.jpg,.jpeg"
                        onChange={handleFileInput}
                        className="hidden"
                        id="gov-doc-upload"
                        disabled={uploading}
                      />
                      <label
                        htmlFor="gov-doc-upload"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 transition-colors cursor-pointer"
                      >
                        <FileText className="w-5 h-5" />
                        Select File
                      </label>
                      <p className="text-xs text-gray-400 mt-4">
                        Supported: PDF, PNG, JPG (Max 10MB)
                      </p>
                    </>
                  )}
                </div>
              )}

              {/* Success State */}
              {uploadedDocumentId && (
                <div className="space-y-4">
                  <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
                    <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-3" />
                    <h3 className="text-lg font-semibold text-green-800 mb-2">Document Uploaded!</h3>
                    <p className="text-sm text-green-700">
                      Ask questions about this document using the chatbot below.
                    </p>
                  </div>

                  {/* Chatbot for this document */}
                  <div className="border border-gray-200 rounded-xl p-4 bg-gray-50">
                    <p className="text-sm font-medium text-gray-700 mb-2">Try asking:</p>
                    <ul className="text-sm text-gray-600 space-y-1 mb-4">
                      <li>• "What does this document mean?"</li>
                      <li>• "Who is eligible?"</li>
                      <li>• "What are the deadlines?"</li>
                      <li>• "What documents are required?"</li>
                    </ul>
                    <Chatbot govDocumentId={uploadedDocumentId} currentPage="goveasy" />
                  </div>

                  <button
                    onClick={() => {
                      setUploadedDocumentId(null);
                      setIsOpen(false);
                    }}
                    className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors"
                  >
                    Upload Another Document
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

