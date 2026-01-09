'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { approvalApi, type ApprovalResponse } from '@/lib/api';
import toast from 'react-hot-toast';
import {
  ArrowLeft, CheckCircle, XCircle, AlertTriangle,
  FileText, Shield, ClipboardCheck, TrendingUp
} from 'lucide-react';
import Chatbot from '@/components/Chatbot';

function ApprovalPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const batchId = searchParams.get('batch_id') || '';

  const [approval, setApproval] = useState<ApprovalResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!batchId) {
      toast.error('Batch ID missing');
      router.push('/');
      return;
    }

    const fetchApproval = async () => {
      try {
        const data = await approvalApi.get(batchId);
        setApproval(data);
      } catch (err) {
        console.error(err);
        const error = err as { response?: { data?: { detail?: string } } };
        toast.error(error.response?.data?.detail || 'Failed to load approval data');
      } finally {
        setLoading(false);
      }
    };

    fetchApproval();
  }, [batchId, router]);

  const getModeDisplay = (mode: string) => {
    const modeMap: Record<string, string> = {
      'aicte': 'AICTE',
      'nba': 'NBA',
      'naac': 'NAAC',
      'nirf': 'NIRF',
      'ugc': 'UGC',
      'mixed': 'Mixed Mode'
    };
    return modeMap[mode.toLowerCase()] || mode.toUpperCase();
  };

  const getReadinessColor = (score: number) => {
    if (score >= 80) return 'text-secondary';
    if (score >= 50) return 'text-primary';
    return 'text-accent';
  };

  const getReadinessBg = (score: number) => {
    if (score >= 80) return 'bg-secondary-50 border-secondary';
    if (score >= 50) return 'bg-primary-50 border-primary';
    return 'bg-accent-50 border-accent';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-soft flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 bg-primary-100 rounded-2xl flex items-center justify-center animate-pulse">
            <ClipboardCheck className="w-8 h-8 text-primary" />
          </div>
          <p className="text-gray-600">Loading approval analysis...</p>
        </div>
      </div>
    );
  }

  if (!approval) {
    return (
      <div className="min-h-screen bg-gradient-soft flex items-center justify-center">
        <div className="text-center bg-white rounded-3xl shadow-soft-lg p-12">
          <XCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Approval Data Not Available</h2>
          <p className="text-gray-600 mb-6">Unable to load approval classification and readiness data.</p>
          <button
            onClick={() => router.push(`/dashboard?batch_id=${batchId}`)}
            className="btn-primary inline-flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-soft py-8 relative">
      {/* Decorative Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="shape-blob w-96 h-96 bg-primary-100 top-0 right-0 translate-x-1/3 -translate-y-1/3 opacity-40" />
        <div className="shape-blob w-72 h-72 bg-secondary-50 bottom-1/4 left-0 -translate-x-1/2 opacity-40" />
      </div>

      <div className="container mx-auto px-4 max-w-6xl relative z-10">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => router.back()}
            className="p-2 bg-white rounded-xl shadow-soft hover:shadow-soft-lg transition-all"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-800">Approval Readiness Analysis</h1>
            <p className="text-gray-600">Mode: {getModeDisplay(approval.mode)} • Batch: {batchId.slice(-12)}</p>
          </div>
        </div>

        {/* Classification Card */}
        <div className="bg-white rounded-3xl shadow-soft-lg p-8 mb-8 border border-gray-100">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary-light rounded-xl flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-xl font-bold text-gray-800">Approval Classification</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-gray-500 mb-1">Category</p>
              <p className="text-lg font-semibold text-gray-800 uppercase">
                {approval.classification.category || 'Not Detected'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Subtype</p>
              <p className="text-lg font-semibold text-gray-800 capitalize">
                {approval.classification.subtype || 'Not Detected'}
              </p>
            </div>
          </div>

          {approval.classification.signals && approval.classification.signals.length > 0 && (
            <div className="mt-6">
              <p className="text-sm text-gray-500 mb-2">Detection Signals</p>
              <div className="flex flex-wrap gap-2">
                {approval.classification.signals.map((signal, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-primary-50 text-primary rounded-full text-sm border border-primary-100"
                  >
                    {signal}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Readiness Score Card */}
        <div className={`bg-white rounded-3xl shadow-soft-lg p-8 mb-8 border-2 ${getReadinessBg(approval.readiness_score)}`}>
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-secondary to-secondary-light rounded-xl flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-xl font-bold text-gray-800">Approval Readiness Score</h2>
          </div>

          <div className="flex flex-col md:flex-row items-center gap-8">
            {/* Score Circle */}
            <div className="relative w-40 h-40 flex-shrink-0">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="80"
                  cy="80"
                  r="70"
                  stroke="#E5E7EB"
                  strokeWidth="12"
                  fill="none"
                />
                <circle
                  cx="80"
                  cy="80"
                  r="70"
                  stroke={
                    approval.readiness_score >= 80 ? '#059669' :
                      approval.readiness_score >= 50 ? '#0D9488' : '#F97316'
                  }
                  strokeWidth="12"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray={`${approval.readiness_score * 4.4} 440`}
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-3xl font-bold ${getReadinessColor(approval.readiness_score)}`}>
                  {approval.readiness_score.toFixed(0)}%
                </span>
                <span className="text-sm text-gray-500">Ready</span>
              </div>
            </div>

            <div className="flex-1">
              <div className="flex items-center gap-4 mb-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-secondary" />
                  <span className="text-gray-700">
                    <strong>{approval.present}</strong> documents present
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <XCircle className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-700">
                    <strong>{approval.required - approval.present}</strong> documents missing
                  </span>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-sm text-gray-500 mb-2">
                  Progress: {approval.present} / {approval.required} required documents
                </p>
                <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-primary to-secondary transition-all duration-1000"
                    style={{ width: `${(approval.present / approval.required) * 100}%` }}
                  />
                </div>
              </div>

              {approval.recommendation && (
                <div className="bg-gray-50 p-4 rounded-2xl border border-gray-100">
                  <p className="text-sm font-medium text-gray-700 mb-1">Recommendation</p>
                  <p className="text-sm text-gray-600">{approval.recommendation}</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Required Documents */}
        <div className="bg-white rounded-3xl shadow-soft-lg p-8 mb-8 border border-gray-100">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-xl font-bold text-gray-800">Required Documents</h2>
            <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
              {approval.required_documents.length} total
            </span>
          </div>

          {approval.required_documents.length > 0 ? (
            <div className="space-y-3">
              {approval.required_documents.map((doc, idx) => {
                const isPresent = approval.documents_found.includes(doc);
                const docDetails = approval.document_details.find(d => d.document_key === doc || d.document_name === doc);

                return (
                  <div
                    key={idx}
                    className={`p-4 rounded-2xl border-2 transition-all ${
                      isPresent
                        ? 'bg-secondary-50 border-secondary-light'
                        : 'bg-red-50 border-red-200'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          {isPresent ? (
                            <CheckCircle className="w-5 h-5 text-secondary flex-shrink-0" />
                          ) : (
                            <XCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                          )}
                          <h3 className="font-semibold text-gray-800">
                            {approval.required_documents_readable?.[idx] || doc}
                          </h3>
                        </div>
                        {docDetails && (
                          <div className="ml-7 text-sm text-gray-600">
                            <p>
                              Confidence: <span className="font-medium">{(docDetails.confidence * 100).toFixed(0)}%</span>
                            </p>
                          </div>
                        )}
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
                          isPresent
                            ? 'bg-secondary text-white'
                            : 'bg-red-200 text-red-800'
                        }`}
                      >
                        {isPresent ? 'Present' : 'Missing'}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p>No required documents defined for this approval type.</p>
            </div>
          )}
        </div>

        {/* Missing Documents Summary */}
        {approval.missing_documents.length > 0 && (
          <div className="bg-red-50 border-2 border-red-200 rounded-3xl shadow-soft-lg p-8 mb-8">
            <div className="flex items-center gap-3 mb-6">
              <AlertTriangle className="w-6 h-6 text-red-600" />
              <h2 className="text-xl font-bold text-red-800">Missing Documents</h2>
              <span className="px-3 py-1 bg-red-200 text-red-800 rounded-full text-sm font-medium">
                {approval.missing_documents.length} missing
              </span>
            </div>

            <div className="space-y-2">
              {approval.missing_documents_readable && approval.missing_documents_readable.length > 0 ? (
                approval.missing_documents_readable.map((doc, idx) => (
                  <div key={idx} className="flex items-center gap-2 p-3 bg-white rounded-xl border border-red-200">
                    <XCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                    <p className="text-gray-800">{doc}</p>
                  </div>
                ))
              ) : (
                approval.missing_documents.map((doc, idx) => (
                  <div key={idx} className="flex items-center gap-2 p-3 bg-white rounded-xl border border-red-200">
                    <XCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                    <p className="text-gray-800">{doc}</p>
                  </div>
                ))
              )}
            </div>

            <div className="mt-6 p-4 bg-white rounded-xl border border-red-200">
              <p className="text-sm text-red-700">
                <strong>Action Required:</strong> Upload the missing documents to improve your approval readiness score.
              </p>
            </div>
          </div>
        )}

        {/* Present Documents Summary */}
        {approval.documents_found.length > 0 && (
          <div className="bg-secondary-50 border-2 border-secondary rounded-3xl shadow-soft-lg p-8 mb-8">
            <div className="flex items-center gap-3 mb-6">
              <CheckCircle className="w-6 h-6 text-secondary" />
              <h2 className="text-xl font-bold text-secondary-dark">Present Documents</h2>
              <span className="px-3 py-1 bg-secondary text-white rounded-full text-sm font-medium">
                {approval.documents_found.length} found
              </span>
            </div>

            <div className="grid md:grid-cols-2 gap-3">
              {approval.documents_found.map((doc, idx) => {
                const docDetails = approval.document_details.find(d => d.document_key === doc || d.document_name === doc);
                return (
                  <div key={idx} className="flex items-center gap-2 p-3 bg-white rounded-xl border border-secondary-light">
                    <CheckCircle className="w-5 h-5 text-secondary flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-gray-800 font-medium">{doc}</p>
                      {docDetails && (
                        <p className="text-xs text-gray-500">
                          Confidence: {(docDetails.confidence * 100).toFixed(0)}%
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Final Recommendation */}
        {approval.recommendation && (
          <div className="bg-gradient-to-r from-primary to-primary-light rounded-3xl shadow-soft-lg p-8 text-white">
            <div className="flex items-center gap-3 mb-4">
              <ClipboardCheck className="w-6 h-6" />
              <h2 className="text-xl font-bold">Final Recommendation</h2>
            </div>
            <p className="text-lg leading-relaxed">{approval.recommendation}</p>
          </div>
        )}

        {/* Navigation */}
        <div className="mt-8 flex flex-wrap gap-4">
          <button
            onClick={() => router.push(`/dashboard?batch_id=${batchId}`)}
            className="btn-primary inline-flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </button>
          <button
            onClick={() => router.push(`/compare?batch_ids=${batchId}`)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-secondary-50 text-secondary border border-secondary rounded-xl font-medium hover:bg-secondary hover:text-white transition-all"
          >
            <TrendingUp className="w-4 h-4" />
            Compare
          </button>
        </div>
      </div>

      {/* Chatbot */}
      {batchId && <Chatbot batchId={batchId} currentPage="approval" />}
    </div>
  );
}

export default function ApprovalPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-soft flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 bg-primary-100 rounded-2xl flex items-center justify-center animate-pulse">
            <ClipboardCheck className="w-8 h-8 text-primary" />
          </div>
          <p className="text-gray-600">Loading approval analysis...</p>
        </div>
      </div>
    }>
      <ApprovalPageContent />
    </Suspense>
  );
}

