'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Award, FileText, Users, BarChart, CheckCircle, AlertCircle, TrendingUp } from 'lucide-react';
import ProtectedRoute from '@/components/ProtectedRoute';

function NBADashboardContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const batchId = searchParams.get('batch_id');

    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>(null);

    useEffect(() => {
        const fetchData = async () => {
            if (!batchId) return;

            try {
                // Try to fetch NBA specific data
                const response = await fetch(`/api/nba/dashboard/${batchId}`);
                if (response.ok) {
                    const result = await response.json();
                    setData(result);
                } else {
                    // Use demo data
                    setData({
                        institution_name: "Demo Engineering College",
                        program_name: "B.Tech Computer Science",
                        peos: [
                            { id: 1, description: "Graduates will demonstrate competence in core areas", status: "achieved" },
                            { id: 2, description: "Graduates will be able to work effectively in teams", status: "achieved" },
                            { id: 3, description: "Graduates will engage in lifelong learning", status: "partial" }
                        ],
                        pos: [
                            { id: 1, description: "Engineering Knowledge", score: 85 },
                            { id: 2, description: "Problem Analysis", score: 78 },
                            { id: 3, description: "Design/Development", score: 82 }
                        ],
                        criteria: [
                            { name: "Vision, Mission and PEOs", score: 88, weight: 100 },
                            { name: "Program Curriculum", score: 85, weight: 225 },
                            { name: "Program Outcomes", score: 82, weight: 200 },
                            { name: "Students' Performance", score: 78, weight: 150 },
                            { name: "Faculty Information", score: 90, weight: 200 },
                            { name: "Facilities and Technical Support", score: 75, weight: 125 }
                        ],
                        overall_score: 82.5,
                        accreditation_status: "Likely Accredited"
                    });
                }
            } catch (error) {
                console.error('Error fetching NBA data:', error);
                // Use demo data on error
                setData({
                    institution_name: "Demo Engineering College",
                    program_name: "B.Tech Computer Science",
                    overall_score: 82.5,
                    accreditation_status: "Likely Accredited",
                    peos: [],
                    pos: [],
                    criteria: []
                });
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [batchId]);

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

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-soft flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-3 border-secondary border-t-transparent" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-soft py-12">
            <div className="container mx-auto px-4 max-w-7xl">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full shadow-soft mb-4 border border-secondary-100">
                        <Award className="w-4 h-4 text-secondary" />
                        <span className="text-sm font-medium text-secondary-dark">NBA Accreditation</span>
                    </div>
                    <h1 className="text-4xl font-bold text-gray-800 mb-3">
                        {data?.institution_name || 'Institution Dashboard'}
                    </h1>
                    <p className="text-gray-600">{data?.program_name || 'Program Evaluation'}</p>
                </div>

                {/* Overall Score Card */}
                <div className="bg-white rounded-3xl shadow-soft-lg p-8 mb-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-2xl font-bold text-gray-800">Overall NBA Score</h2>
                            <p className="text-gray-600">{data?.accreditation_status}</p>
                        </div>
                        <div className="text-right">
                            <div className="text-5xl font-bold text-secondary">{data?.overall_score || 0}</div>
                            <div className="text-gray-500">/ 100</div>
                        </div>
                    </div>
                </div>

                {/* Criteria Grid */}
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                    {(data?.criteria || []).map((criterion: any, index: number) => (
                        <div key={index} className="bg-white rounded-2xl shadow-soft p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="font-semibold text-gray-800">{criterion.name}</h3>
                                <span className="text-xs bg-secondary-50 text-secondary px-2 py-1 rounded-full">
                                    Weight: {criterion.weight}
                                </span>
                            </div>
                            <div className="flex items-center gap-4">
                                <div className="flex-1 bg-gray-200 rounded-full h-3">
                                    <div
                                        className="bg-secondary rounded-full h-3 transition-all duration-500"
                                        style={{ width: `${criterion.score}%` }}
                                    />
                                </div>
                                <span className="font-bold text-secondary">{criterion.score}%</span>
                            </div>
                        </div>
                    ))}
                </div>

                {/* PEOs Section */}
                {data?.peos && data.peos.length > 0 && (
                    <div className="bg-white rounded-3xl shadow-soft-lg p-8 mb-8">
                        <h2 className="text-xl font-bold text-gray-800 mb-6">Program Educational Objectives (PEOs)</h2>
                        <div className="space-y-4">
                            {data.peos.map((peo: any) => (
                                <div key={peo.id} className="flex items-start gap-4 p-4 bg-gray-50 rounded-xl">
                                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${peo.status === 'achieved' ? 'bg-green-100' : 'bg-yellow-100'
                                        }`}>
                                        {peo.status === 'achieved' ? (
                                            <CheckCircle className="w-5 h-5 text-green-600" />
                                        ) : (
                                            <AlertCircle className="w-5 h-5 text-yellow-600" />
                                        )}
                                    </div>
                                    <div>
                                        <p className="font-medium text-gray-800">PEO {peo.id}</p>
                                        <p className="text-gray-600 text-sm">{peo.description}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Navigation */}
                <div className="flex justify-center gap-4">
                    <button
                        onClick={() => router.push('/')}
                        className="px-6 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors"
                    >
                        Back to Home
                    </button>
                    <button
                        onClick={() => router.push(`/reports?batch_id=${batchId}`)}
                        className="px-6 py-3 bg-secondary text-white rounded-xl hover:bg-secondary-dark transition-colors"
                    >
                        Generate Report
                    </button>
                </div>
            </div>
        </div>
    );
}

export default function NBADashboardPage() {
    return (
        <ProtectedRoute>
            <Suspense fallback={
                <div className="min-h-screen bg-gradient-soft flex items-center justify-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-3 border-secondary border-t-transparent" />
                </div>
            }>
                <NBADashboardContent />
            </Suspense>
        </ProtectedRoute>
    );
}
