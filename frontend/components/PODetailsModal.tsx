'use client';

import { useState, useEffect } from 'react';
import { X, Calculator, AlertTriangle, CheckCircle, BookOpen, TrendingUp, Scale } from 'lucide-react';

interface PODetailsModalProps {
    isOpen: boolean;
    onClose: () => void;
    batchId: string;
    poId: string;
}

interface ContributingCO {
    co_id: string;
    course_name: string;
    attainment: number | null;
    mapping_level: number;
    weighted_contribution: number;
}

interface EvidenceSnippet {
    source_document: string;
    page: number | null;
    snippet: string;
}

interface PODrilldownData {
    po_id: string;
    po_name: string;
    direct_attainment: number | null;
    indirect_attainment: number | null;
    final_attainment: number | null;
    status: string;
    formula_used: string;
    direct_weight: number;
    indirect_weight: number;
    contributing_cos: ContributingCO[];
    evidence_snippets: EvidenceSnippet[];
    improvement_action?: string | null;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000/api';

export default function PODetailsModal({ isOpen, onClose, batchId, poId }: PODetailsModalProps) {
    const [data, setData] = useState<PODrilldownData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (isOpen && batchId && poId) {
            fetchPODetails();
        }
    }, [isOpen, batchId, poId]);

    const fetchPODetails = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/nba/${batchId}/po/${poId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('firebase_token') || ''}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Failed to load PO details (${response.status})`);
            }

            const result = await response.json();
            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load PO details');
            console.error('Error fetching PO details:', err);
        } finally {
            setLoading(false);
        }
    };

    // Render value or "Insufficient Evidence"
    const renderValue = (value: number | null | undefined, suffix: string = '%') => {
        if (value === null || value === undefined) {
            return <span className="text-amber-600 italic">Insufficient Evidence</span>;
        }
        return <span className="font-bold">{value.toFixed(1)}{suffix}</span>;
    };

    // Get status color
    const getStatusColor = (status: string) => {
        const s = status.toLowerCase().replace(/_/g, ' ');
        if (s === 'attained') return 'bg-green-100 text-green-800 border-green-300';
        if (s.includes('partial')) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
        if (s.includes('not attained')) return 'bg-red-100 text-red-800 border-red-300';
        return 'bg-gray-100 text-gray-600 border-gray-300';
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gradient-to-r from-purple-600 to-purple-500 text-white">
                    <div>
                        <h2 className="text-2xl font-bold">{poId} Details</h2>
                        <p className="text-white/80 text-sm mt-1">Program Outcome Drill-Down • Backend Data Only</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-full transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Content */}
                <div className="overflow-y-auto max-h-[calc(90vh-120px)] p-6">
                    {loading ? (
                        <div className="flex items-center justify-center py-12">
                            <div className="text-center">
                                <div className="w-10 h-10 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                                <p className="text-gray-600">Loading from backend...</p>
                            </div>
                        </div>
                    ) : error ? (
                        <div className="text-center py-12">
                            <AlertTriangle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                            <h3 className="text-xl font-bold text-red-800 mb-2">Failed to Load PO Details</h3>
                            <p className="text-red-600">{error}</p>
                        </div>
                    ) : data ? (
                        <div className="space-y-8">
                            {/* Summary Card */}
                            <div className="bg-gray-50 rounded-2xl p-6">
                                <div className="flex items-start gap-6">
                                    <div className="flex-1">
                                        <h3 className="text-xl font-bold text-gray-800 mb-2">{data.po_name}</h3>
                                        <span className={`inline-block px-4 py-1 rounded-full text-sm font-medium border ${getStatusColor(data.status)}`}>
                                            {data.status.replace(/_/g, ' ')}
                                        </span>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-sm text-gray-500 mb-1">Final Attainment</div>
                                        <div className="text-4xl font-bold text-purple-600">
                                            {data.final_attainment !== null ? `${data.final_attainment.toFixed(1)}%` : 'N/A'}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Attainment Breakdown */}
                            <div className="grid md:grid-cols-2 gap-4">
                                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                                    <div className="text-sm text-blue-600 font-medium mb-1">Direct Attainment</div>
                                    <div className="text-2xl">
                                        {renderValue(data.direct_attainment)}
                                    </div>
                                    <div className="text-xs text-blue-500 mt-1">Weight: {(data.direct_weight * 100).toFixed(0)}%</div>
                                </div>
                                <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                                    <div className="text-sm text-green-600 font-medium mb-1">Indirect Attainment</div>
                                    <div className="text-2xl">
                                        {renderValue(data.indirect_attainment)}
                                    </div>
                                    <div className="text-xs text-green-500 mt-1">Weight: {(data.indirect_weight * 100).toFixed(0)}%</div>
                                </div>
                            </div>

                            {/* Formula */}
                            {data.formula_used && (
                                <div className="bg-purple-50 border border-purple-200 rounded-2xl p-5">
                                    <h3 className="font-bold text-purple-800 mb-3 flex items-center gap-2">
                                        <Calculator className="w-5 h-5" />
                                        Formula Used
                                    </h3>
                                    <code className="block bg-white border border-purple-100 p-4 rounded-xl font-mono text-sm text-gray-800">
                                        {data.formula_used}
                                    </code>
                                </div>
                            )}

                            {/* Contributing COs Table */}
                            {data.contributing_cos && data.contributing_cos.length > 0 && (
                                <div>
                                    <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                                        <Scale className="w-5 h-5 text-purple-600" />
                                        Contributing Course Outcomes
                                    </h3>
                                    <div className="border border-gray-200 rounded-2xl overflow-hidden">
                                        <table className="w-full text-sm">
                                            <thead className="bg-gray-100">
                                                <tr>
                                                    <th className="text-left py-3 px-4 font-semibold text-gray-700">CO</th>
                                                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Course</th>
                                                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Attainment</th>
                                                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Mapping Level</th>
                                                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Contribution</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {data.contributing_cos.map((co, idx) => (
                                                    <tr key={idx} className="border-t border-gray-100">
                                                        <td className="py-3 px-4 font-medium text-purple-600">{co.co_id}</td>
                                                        <td className="py-3 px-4 text-gray-600">{co.course_name}</td>
                                                        <td className="py-3 px-4 text-right">
                                                            {co.attainment !== null ? `${co.attainment.toFixed(1)}%` :
                                                                <span className="text-amber-600 italic text-xs">No data</span>}
                                                        </td>
                                                        <td className="py-3 px-4 text-right">
                                                            <span className={`px-2 py-1 rounded text-xs font-medium ${co.mapping_level === 3 ? 'bg-green-100 text-green-700' :
                                                                    co.mapping_level === 2 ? 'bg-yellow-100 text-yellow-700' :
                                                                        'bg-gray-100 text-gray-600'
                                                                }`}>
                                                                Level {co.mapping_level}
                                                            </span>
                                                        </td>
                                                        <td className="py-3 px-4 text-right font-semibold text-purple-600">
                                                            {co.weighted_contribution.toFixed(2)}
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}

                            {/* Evidence Snippets */}
                            {data.evidence_snippets && data.evidence_snippets.length > 0 ? (
                                <div>
                                    <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                                        <BookOpen className="w-5 h-5 text-purple-600" />
                                        Evidence from Documents
                                    </h3>
                                    <div className="space-y-3">
                                        {data.evidence_snippets.map((ev, idx) => (
                                            <div key={idx} className="bg-green-50 border border-green-200 rounded-xl p-4">
                                                <div className="flex items-center gap-2 mb-2 text-green-700 font-medium">
                                                    <CheckCircle className="w-4 h-4" />
                                                    <span>{ev.source_document}</span>
                                                    {ev.page && <span className="text-sm text-green-500">• Page {ev.page}</span>}
                                                </div>
                                                <p className="text-gray-700 text-sm italic">"{ev.snippet}"</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ) : (
                                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                                    <div className="flex items-center gap-2 text-amber-700 font-medium">
                                        <AlertTriangle className="w-5 h-5" />
                                        Evidence Not Available
                                    </div>
                                    <p className="text-amber-600 text-sm mt-1">
                                        No direct evidence snippets found in uploaded documents for this PO.
                                    </p>
                                </div>
                            )}

                            {/* Improvement Action */}
                            {data.improvement_action && (
                                <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
                                    <h3 className="font-bold text-orange-800 mb-2 flex items-center gap-2">
                                        <TrendingUp className="w-5 h-5" />
                                        Recommended Improvement Action
                                    </h3>
                                    <p className="text-orange-700">{data.improvement_action}</p>
                                </div>
                            )}

                            {/* Audit Notice */}
                            <div className="bg-gray-100 border border-gray-200 rounded-xl p-4 text-center">
                                <p className="text-sm text-gray-600">
                                    <CheckCircle className="w-4 h-4 inline mr-1 text-green-600" />
                                    All values fetched from backend API. No frontend calculations.
                                </p>
                            </div>
                        </div>
                    ) : null}
                </div>
            </div>
        </div>
    );
}
