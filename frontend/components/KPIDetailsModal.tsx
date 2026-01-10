'use client';

import { useState, useEffect } from 'react';
import { X, Calculator, FileText, AlertTriangle, CheckCircle, BookOpen, Scale, HelpCircle } from 'lucide-react';
import { kpiDetailsApi, type KPIDetailedResponse } from '@/lib/api';

interface KPIDetailsModalProps {
    isOpen: boolean;
    onClose: () => void;
    batchId: string;
    kpiName: string;
}

interface EvidenceData {
    snippet: string;
    page: number | null;
    source_doc: string;
}

interface ParameterData {
    name: string;
    display_name: string;
    extracted: number | null;
    norm: number | null;
    weight: number;
    contrib: number;
    unit: string;
    missing: boolean;
    evidence: EvidenceData;
}

interface CalculationStep {
    step: number;
    description: string;
    formula: string;
    result: number | null;
}

export default function KPIDetailsModal({ isOpen, onClose, batchId, kpiName }: KPIDetailsModalProps) {
    const [data, setData] = useState<KPIDetailedResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (isOpen && batchId && kpiName) {
            fetchKPIDetails();
        }
    }, [isOpen, batchId, kpiName]);

    const fetchKPIDetails = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await kpiDetailsApi.get(batchId, kpiName);

            // Map kpiName to the response key
            const kpiKeyMap: Record<string, string> = {
                'fsr': 'fsr',
                'infrastructure': 'infrastructure',
                'placement': 'placement',
                'lab': 'lab_compliance',
                'overall': 'overall'
            };

            const responseKey = kpiKeyMap[kpiName] || kpiName;
            const kpiData = (response as any)[responseKey];

            if (kpiData) {
                // Transform the nested KPI data to match our expected format
                setData({
                    kpi_type: kpiData.kpi_key || kpiName,
                    kpi_name: kpiData.kpi_name || kpiName.replace(/_/g, ' ').toUpperCase(),
                    score: kpiData.final_score ?? null,
                    weightages: {},
                    parameters: (kpiData.parameters || []).map((p: any) => ({
                        name: p.parameter_name || '',
                        display_name: p.display_name || p.parameter_name || '',
                        extracted: p.raw_value ?? p.normalized_value ?? null,
                        norm: p.normalized_value ?? p.raw_value ?? null,
                        weight: p.weight ?? 0,
                        contrib: p.contribution ?? p.score ?? 0,
                        unit: p.unit || '',
                        missing: p.missing ?? (p.raw_value === null && p.normalized_value === null),
                        evidence: {
                            snippet: p.evidence_snippet || p.note || '',
                            page: p.evidence_page ?? null,
                            source_doc: p.source_document || ''
                        }
                    })),
                    calculation_steps: (kpiData.formula_steps || []).map((s: any, i: number) => ({
                        step: s.step_number ?? i + 1,
                        description: s.description || '',
                        formula: s.formula || '',
                        result: s.result ?? null
                    })),
                    formula: kpiData.formula_text || '',
                    evidence: {},
                    included_kpis: [],
                    excluded_kpis: kpiData.missing_parameters || []
                });
            } else {
                setError('KPI data not found in backend response');
            }
        } catch (err) {
            setError('Failed to load KPI details from backend');
            console.error('Error fetching KPI details:', err);
        } finally {
            setLoading(false);
        }
    };

    // Check if a parameter has valid evidence
    const hasValidEvidence = (param: ParameterData): boolean => {
        return !!(param?.evidence?.snippet && param.evidence.snippet.length > 3);
    };

    // Render evidence block
    const renderEvidence = (param: ParameterData) => {
        if (!param?.evidence || !param.evidence.snippet) {
            return (
                <div className="flex items-center gap-1 text-amber-600">
                    <AlertTriangle className="w-3 h-3" />
                    <span className="text-xs italic">No evidence</span>
                </div>
            );
        }

        return (
            <div className="bg-green-50 border border-green-200 rounded-lg p-2 text-xs">
                <div className="flex items-center gap-1 text-green-700 font-medium mb-1">
                    <CheckCircle className="w-3 h-3" />
                    Evidence Found
                </div>
                <p className="text-gray-700 line-clamp-2" title={param.evidence.snippet}>
                    "{param.evidence.snippet.slice(0, 100)}{param.evidence.snippet.length > 100 ? '...' : ''}"
                </p>
                <div className="flex gap-3 mt-1 text-gray-500">
                    {param.evidence.source_doc && (
                        <span>📄 {param.evidence.source_doc}</span>
                    )}
                    {param.evidence.page !== null && param.evidence.page > 0 && (
                        <span>📑 Page {param.evidence.page}</span>
                    )}
                </div>
            </div>
        );
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="bg-white rounded-3xl shadow-2xl max-w-5xl w-full mx-4 max-h-[90vh] overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gradient-to-r from-primary to-primary-light text-white">
                    <div>
                        <h2 className="text-2xl font-bold">{data?.kpi_name || 'KPI Details'}</h2>
                        <p className="text-white/80 text-sm mt-1">Audit-Ready Backend Computation</p>
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
                                <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                                <p className="text-gray-600">Loading from backend...</p>
                            </div>
                        </div>
                    ) : error ? (
                        <div className="text-center py-12">
                            <AlertTriangle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                            <h3 className="text-xl font-bold text-red-800 mb-2">Failed to Load KPI Details</h3>
                            <p className="text-red-600">{error}</p>
                            <p className="text-gray-500 text-sm mt-4">This may indicate the batch was not fully processed or the KPI is not available.</p>
                        </div>
                    ) : data ? (
                        <div className="space-y-8">
                            {/* Score Summary */}
                            <div className="flex items-center gap-6 bg-gray-50 rounded-2xl p-6">
                                <div className="w-28 h-28 rounded-full border-8 border-primary flex items-center justify-center bg-white">
                                    {data.score != null ? (
                                        <span className="text-3xl font-bold text-primary">{data.score.toFixed(0)}</span>
                                    ) : (
                                        <span className="text-lg text-gray-400">N/A</span>
                                    )}
                                </div>
                                <div className="flex-1">
                                    {data.score != null ? (
                                        <>
                                            <p className="text-2xl font-bold text-gray-800">{data.score.toFixed(2)} / 100</p>
                                            <p className="text-gray-600 mt-1">Score computed from extracted document data</p>
                                        </>
                                    ) : (
                                        <>
                                            <p className="text-xl font-bold text-amber-700 flex items-center gap-2">
                                                <AlertTriangle className="w-5 h-5" />
                                                Insufficient Evidence
                                            </p>
                                            <p className="text-gray-600 mt-1">Required data not found in uploaded documents</p>
                                        </>
                                    )}
                                </div>
                            </div>

                            {/* Formula Section */}
                            {data.formula && (
                                <div className="bg-blue-50 border border-blue-200 rounded-2xl p-5">
                                    <h3 className="font-bold text-blue-800 mb-3 flex items-center gap-2">
                                        <Calculator className="w-5 h-5" />
                                        Formula Used (Computation Method)
                                    </h3>
                                    <code className="block bg-white border border-blue-100 p-4 rounded-xl font-mono text-sm text-gray-800">
                                        {data.formula}
                                    </code>
                                </div>
                            )}

                            {/* Input Parameters Table with Evidence */}
                            {data.parameters && data.parameters.length > 0 && (
                                <div>
                                    <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                                        <Scale className="w-5 h-5 text-primary" />
                                        Input Values & Evidence (All from Backend)
                                    </h3>
                                    <div className="border border-gray-200 rounded-2xl overflow-hidden">
                                        <table className="w-full text-sm">
                                            <thead className="bg-gray-100">
                                                <tr>
                                                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Parameter</th>
                                                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Extracted Value</th>
                                                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Weight</th>
                                                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Contribution</th>
                                                    <th className="text-left py-3 px-4 font-semibold text-gray-700 min-w-[250px]">Evidence</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {(data.parameters as ParameterData[]).map((param, idx) => (
                                                    <tr key={idx} className={`border-t border-gray-100 ${param?.missing ? 'bg-red-50' : ''}`}>
                                                        <td className="py-3 px-4">
                                                            <div className="font-medium text-gray-800">{param?.display_name || '—'}</div>
                                                            {param?.missing && (
                                                                <span className="text-xs text-red-600 flex items-center gap-1 mt-1">
                                                                    <AlertTriangle className="w-3 h-3" /> Missing
                                                                </span>
                                                            )}
                                                        </td>
                                                        <td className="py-3 px-4 text-right">
                                                            {param?.extracted != null ? (
                                                                <span className="font-mono font-semibold text-gray-800">
                                                                    {param.extracted}{param?.unit ? ` ${param.unit}` : ''}
                                                                </span>
                                                            ) : (
                                                                <span className="text-amber-600 italic text-xs">Insufficient Evidence</span>
                                                            )}
                                                        </td>
                                                        <td className="py-3 px-4 text-right text-gray-600">
                                                            {param?.weight != null && param.weight > 0 ? `${(param.weight * 100).toFixed(0)}%` : '—'}
                                                        </td>
                                                        <td className="py-3 px-4 text-right font-semibold text-primary">
                                                            {param?.contrib != null && param.contrib !== 0 ? param.contrib.toFixed(2) : '—'}
                                                        </td>
                                                        <td className="py-3 px-4">
                                                            {renderEvidence(param)}
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}

                            {/* Calculation Steps */}
                            {data.calculation_steps && data.calculation_steps.length > 0 && (
                                <div>
                                    <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                                        <BookOpen className="w-5 h-5 text-primary" />
                                        Step-by-Step Calculation
                                    </h3>
                                    <div className="space-y-3">
                                        {(data.calculation_steps as CalculationStep[]).map((step, idx) => (
                                            <div key={step?.step || idx} className="flex items-start gap-4 p-4 bg-gray-50 rounded-xl border border-gray-100">
                                                <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
                                                    {step?.step || idx + 1}
                                                </div>
                                                <div className="flex-1">
                                                    <p className="font-medium text-gray-800">{step?.description || ''}</p>
                                                    <code className="text-sm text-gray-600 font-mono block mt-1">{step?.formula || ''}</code>
                                                    {step?.result != null && (
                                                        <div className="mt-2 text-primary font-bold">
                                                            Result: {step.result}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Missing Parameters Warning */}
                            {data.parameters && (data.parameters as ParameterData[]).some(p => p?.missing) && (
                                <div className="bg-amber-50 border-2 border-amber-300 rounded-2xl p-5">
                                    <h3 className="font-bold text-amber-800 flex items-center gap-2 mb-3">
                                        <AlertTriangle className="w-5 h-5" />
                                        Missing Parameters - Evidence Not Found
                                    </h3>
                                    <p className="text-amber-700 text-sm mb-3">
                                        The following parameters could not be extracted from the uploaded documents:
                                    </p>
                                    <div className="flex flex-wrap gap-2">
                                        {(data.parameters as ParameterData[]).filter(p => p?.missing).map(p => (
                                            <span key={p?.name} className="px-3 py-1 bg-amber-200 text-amber-800 rounded-full text-sm font-medium">
                                                {p?.display_name || 'Unknown'}
                                            </span>
                                        ))}
                                    </div>
                                    <p className="text-amber-600 text-xs mt-3 italic">
                                        Upload documents containing this information to improve the score calculation.
                                    </p>
                                </div>
                            )}

                            {/* Audit Notice */}
                            <div className="bg-gray-100 border border-gray-200 rounded-xl p-4 text-center">
                                <p className="text-sm text-gray-600">
                                    <CheckCircle className="w-4 h-4 inline mr-1 text-green-600" />
                                    All values shown are from backend computation. No frontend calculations.
                                </p>
                            </div>
                        </div>
                    ) : null}
                </div>
            </div>
        </div>
    );
}
