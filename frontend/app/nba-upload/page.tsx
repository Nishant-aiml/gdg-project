'use client';

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Award, Upload, FileText, ArrowRight } from 'lucide-react';
import ProtectedRoute from '@/components/ProtectedRoute';
import toast from 'react-hot-toast';

function NBAUploadContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const batchId = searchParams.get('batch_id');

    const [files, setFiles] = useState<File[]>([]);
    const [uploading, setUploading] = useState(false);
    const [programName, setProgramName] = useState('');
    const [academicYear, setAcademicYear] = useState('');

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFiles = Array.from(e.target.files || []);
        setFiles(prev => [...prev, ...selectedFiles]);
    };

    const handleUpload = async () => {
        if (!batchId) {
            toast.error('Batch ID missing');
            return;
        }

        if (files.length === 0) {
            toast.error('Please select at least one file');
            return;
        }

        setUploading(true);
        try {
            // Upload files
            for (const file of files) {
                const formData = new FormData();
                formData.append('file', file);

                await fetch(`/api/documents/upload/${batchId}`, {
                    method: 'POST',
                    body: formData
                });
                toast.success(`Uploaded: ${file.name}`);
            }

            // Start processing
            await fetch(`/api/processing/start/${batchId}`, { method: 'POST' });
            toast.success('Processing started!');
            router.push(`/processing?batch_id=${batchId}`);
        } catch (error) {
            console.error('Upload error:', error);
            toast.error('Upload failed');
        } finally {
            setUploading(false);
        }
    };

    if (!batchId) {
        return (
            <div className="min-h-screen bg-gradient-soft flex items-center justify-center">
                <div className="text-center bg-white rounded-3xl shadow-soft-lg p-12 max-w-md">
                    <Award className="w-16 h-16 text-secondary mx-auto mb-6" />
                    <p className="text-gray-600 mb-6">No batch selected. Please start from the home page.</p>
                    <button
                        onClick={() => router.push('/')}
                        className="btn-primary"
                    >
                        Go to Home
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-soft py-12">
            <div className="container mx-auto px-4 max-w-4xl">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full shadow-soft mb-4 border border-secondary-100">
                        <Award className="w-4 h-4 text-secondary" />
                        <span className="text-sm font-medium text-secondary-dark">NBA Accreditation</span>
                    </div>
                    <h1 className="text-4xl font-bold text-gray-800 mb-3">
                        Upload NBA Documents
                    </h1>
                    <p className="text-gray-600">
                        Upload Self Assessment Report (SAR) and supporting documents
                    </p>
                </div>

                {/* Program Info */}
                <div className="bg-white rounded-3xl shadow-soft-lg p-8 mb-8">
                    <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                        <FileText className="w-5 h-5 text-secondary" />
                        Program Information
                    </h2>
                    <div className="grid md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Program Name
                            </label>
                            <input
                                type="text"
                                value={programName}
                                onChange={(e) => setProgramName(e.target.value)}
                                placeholder="e.g., B.Tech Computer Science"
                                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Academic Year
                            </label>
                            <input
                                type="text"
                                value={academicYear}
                                onChange={(e) => setAcademicYear(e.target.value)}
                                placeholder="e.g., 2024-25"
                                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent"
                            />
                        </div>
                    </div>
                </div>

                {/* Upload Zone */}
                <div className="bg-white rounded-3xl shadow-soft-lg p-12 text-center mb-8 border-2 border-dashed border-gray-200 hover:border-secondary-light transition-colors">
                    <div className="w-20 h-20 mx-auto mb-6 rounded-3xl bg-gradient-to-br from-secondary-50 to-secondary-100 flex items-center justify-center">
                        <Upload className="w-10 h-10 text-secondary" />
                    </div>
                    <p className="text-xl font-medium text-gray-800 mb-2">
                        Drag & drop files here
                    </p>
                    <p className="text-gray-500 mb-6">or</p>
                    <label className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-secondary to-secondary-light text-white rounded-xl cursor-pointer hover:shadow-lg transition-all font-medium">
                        <FileText className="w-5 h-5" />
                        Browse Files
                        <input
                            type="file"
                            multiple
                            accept=".pdf,.xlsx,.xls,.csv,.docx"
                            onChange={handleFileSelect}
                            className="hidden"
                        />
                    </label>
                    <p className="text-sm text-gray-400 mt-6">
                        Supports PDF, Excel, CSV, Word • Max: 50MB
                    </p>
                </div>

                {/* File List */}
                {files.length > 0 && (
                    <div className="bg-white rounded-3xl shadow-soft-lg p-8 mb-8">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">
                            Selected Files ({files.length})
                        </h3>
                        <div className="space-y-3">
                            {files.map((file, index) => (
                                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                                    <div className="flex items-center gap-3">
                                        <FileText className="w-6 h-6 text-secondary" />
                                        <div>
                                            <p className="font-medium text-gray-800">{file.name}</p>
                                            <p className="text-sm text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => setFiles(prev => prev.filter((_, i) => i !== index))}
                                        className="text-gray-400 hover:text-red-500"
                                    >
                                        ×
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Upload Button */}
                {files.length > 0 && (
                    <div className="text-center">
                        <button
                            onClick={handleUpload}
                            disabled={uploading}
                            className="inline-flex items-center gap-3 px-10 py-4 bg-gradient-to-r from-secondary to-secondary-dark text-white text-lg font-semibold rounded-2xl hover:shadow-lg disabled:opacity-50 transition-all"
                        >
                            {uploading ? (
                                <>
                                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                                    Uploading...
                                </>
                            ) : (
                                <>
                                    Upload & Process
                                    <ArrowRight className="w-5 h-5" />
                                </>
                            )}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default function NBAUploadPage() {
    return (
        <ProtectedRoute>
            <Suspense fallback={
                <div className="min-h-screen bg-gradient-soft flex items-center justify-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-3 border-secondary border-t-transparent" />
                </div>
            }>
                <NBAUploadContent />
            </Suspense>
        </ProtectedRoute>
    );
}
