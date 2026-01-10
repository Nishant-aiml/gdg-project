'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { batchApi } from '@/lib/api';
import toast from 'react-hot-toast';
import { FileText, GraduationCap, Sparkles, Shield, BarChart3, CheckCircle, Layers, Award } from 'lucide-react';
import ProtectedRoute from '@/components/ProtectedRoute';

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [selectedMode, setSelectedMode] = useState<'aicte' | 'nba' | null>(null);

  const handleModeSelect = async (mode: 'aicte' | 'nba') => {
    setLoading(true);
    setSelectedMode(mode);
    try {
      // Create batch with mode only - institution/department can be set during upload
      const batch = await batchApi.create({ mode });
      toast.success(`${mode.toUpperCase()} batch created!`);
      router.push(`/upload?batch_id=${batch.batch_id}`);
    } catch (err: any) {
      console.error('Batch creation error:', err);
      let errorMessage = 'Failed to create batch';

      if (err.response) {
        errorMessage = err.response.data?.detail || err.response.data?.message || `Server error: ${err.response.status}`;
      } else if (err.request) {
        errorMessage = 'No response from server. Please check if the backend is running.';
      } else if (err.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. Please try again.';
      } else if (err.message) {
        errorMessage = err.message;
      }

      toast.error(errorMessage);
      setSelectedMode(null);
    } finally {
      setLoading(false);
    }
  };

  const modes = [
    {
      id: 'aicte' as const,
      name: 'AICTE Mode',
      description: 'Technical education institutions evaluation',
      icon: GraduationCap,
      color: 'primary',
      tag: 'Technical',
      blocks: 10,
      features: ['Faculty', 'Infrastructure', 'Placements', '+7 more']
    },
    {
      id: 'nba' as const,
      name: 'NBA Mode',
      description: 'National Board of Accreditation evaluation',
      icon: Award,
      color: 'secondary',
      tag: 'Accreditation',
      blocks: 8,
      features: ['PEOs/PSOs', 'Faculty Quality', 'Student Performance', '+5 more']
    }
  ];

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-soft relative overflow-hidden">
        {/* Decorative Background Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="shape-blob w-96 h-96 bg-primary-100 top-0 right-0 translate-x-1/2 -translate-y-1/2" />
          <div className="shape-blob w-80 h-80 bg-secondary-50 bottom-0 left-0 -translate-x-1/2 translate-y-1/2" />
          <div className="shape-blob w-64 h-64 bg-accent-50 top-1/2 left-1/4 opacity-30" />
        </div>

        <div className="container mx-auto px-4 py-12 relative z-10">
          {/* Header */}
          <div className="text-center mb-12 animate-fade-in">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full shadow-soft mb-6 border border-primary-100">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium text-primary-dark">AI-Powered Document Analysis</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
              Smart Approval{' '}
              <span className="bg-gradient-to-r from-primary to-primary-light bg-clip-text text-transparent">
                AI
              </span>
            </h1>
            <p className="text-lg text-gray-600 max-w-xl mx-auto">
              Intelligent Document Analysis & Performance Indicators for Accreditation Reviewers
            </p>
          </div>

          {/* Features Row */}
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            {[
              { icon: Shield, label: 'Compliance Check', color: 'text-primary' },
              { icon: BarChart3, label: 'KPI Analysis', color: 'text-secondary' },
              { icon: CheckCircle, label: 'Auto Validation', color: 'text-accent' },
            ].map((feature, index) => (
              <div
                key={index}
                className="flex items-center gap-2 px-4 py-2 bg-white/70 backdrop-blur-sm rounded-full shadow-soft border border-gray-100"
              >
                <feature.icon className={`w-4 h-4 ${feature.color}`} />
                <span className="text-gray-700 font-medium text-sm">{feature.label}</span>
              </div>
            ))}
          </div>

          {/* Mode Selection Cards - 2 Column Grid */}
          <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-6">
            {modes.map((mode) => {
              const Icon = mode.icon;
              const colorClasses: Record<string, { bg: string; text: string; tag: string; card: string; number: string; dot: string }> = {
                primary: {
                  bg: 'from-primary-50 to-primary-100',
                  text: 'text-primary',
                  tag: 'bg-primary-50 text-primary',
                  card: 'bg-primary-50/50',
                  number: 'bg-primary',
                  dot: 'bg-primary'
                },
                secondary: {
                  bg: 'from-secondary-50 to-secondary-100',
                  text: 'text-secondary',
                  tag: 'bg-secondary-50 text-secondary',
                  card: 'bg-secondary-50/50',
                  number: 'bg-secondary',
                  dot: 'bg-secondary'
                }
              };
              const colors = colorClasses[mode.color];

              return (
                <div
                  key={mode.id}
                  onClick={() => !loading && handleModeSelect(mode.id)}
                  className={`group relative bg-white rounded-3xl shadow-soft-lg p-6 cursor-pointer transition-all duration-300 hover:shadow-soft-xl hover:-translate-y-1 border border-gray-100 ${loading && selectedMode === mode.id ? 'ring-2 ring-primary ring-offset-2' : ''} ${loading && selectedMode !== mode.id ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className={`w-14 h-14 bg-gradient-to-br ${colors.bg} rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className={`w-7 h-7 ${colors.text}`} />
                    </div>
                    <div className={`px-2 py-1 ${colors.tag} rounded-full`}>
                      <span className="text-xs font-semibold">{mode.tag}</span>
                    </div>
                  </div>

                  <h2 className="text-xl font-bold text-gray-800 mb-2">{mode.name}</h2>
                  <p className="text-gray-600 text-sm mb-4">
                    {mode.description}
                  </p>

                  <div className={`${colors.card} rounded-xl p-3 mb-4`}>
                    <p className={`text-xs font-semibold mb-2 flex items-center gap-1 ${colors.text}`}>
                      <span className={`w-4 h-4 ${colors.number} rounded-full flex items-center justify-center text-white text-xs`}>
                        {mode.blocks}
                      </span>
                      Blocks Extracted
                    </p>
                    <div className="grid grid-cols-2 gap-1 text-xs text-gray-600">
                      {mode.features.map((feature, idx) => (
                        <div key={idx} className="flex items-center gap-1">
                          <div className={`w-1 h-1 rounded-full ${colors.dot}`} />
                          {feature}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className={`${colors.text} font-semibold text-sm group-hover:translate-x-1 transition-transform`}>
                      Start →
                    </span>
                    {loading && selectedMode === mode.id && (
                      <div className={`animate-spin rounded-full h-4 w-4 border-2 ${colors.text} border-t-transparent`} />
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Footer Info */}
          <div className="max-w-2xl mx-auto mt-12 text-center">
            <p className="text-gray-500 text-sm">
              Select a mode to begin evaluating institutional documents with AI-powered analysis
            </p>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
