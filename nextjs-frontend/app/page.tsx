/**
 * Main RAG Interface Page
 * 
 * Copyright © 2025 Samay Mehar. All Rights Reserved.
 * PROPRIETARY SOFTWARE - PATENT PENDING
 */

'use client';

import { useState } from 'react';
import { UploadSection } from '@/components/upload-section';
import { QueryInput } from '@/components/query-input';
import { ResultsPanel } from '@/components/results-panel';
import { queryRAG, type QueryResponse } from '@/lib/api';
import { Brain, Sparkles } from 'lucide-react';

export default function RAGInterface() {
  const [queryResults, setQueryResults] = useState<QueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleQuery = async (query: string, queryType: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const results = await queryRAG({
        query,
        collection_name: 'multimodal_docs',
        top_k: 5,
        use_rag: true,
      });

      setQueryResults(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Query failed');
      console.error('Query error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 bg-gradient-to-br from-cyan-500 to-emerald-500 rounded-lg flex items-center justify-center">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-100">VectorMind</h1>
              <p className="text-xs text-slate-400">Multimodal RAG System</p>
            </div>
            <div className="flex-1" />
            <div className="flex items-center space-x-2 text-sm text-slate-400">
              <Sparkles className="h-4 w-4 text-cyan-500" />
              <span>Powered by AI</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Sidebar - Upload & Query */}
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 backdrop-blur-sm">
              <UploadSection />
            </div>

            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 backdrop-blur-sm">
              <QueryInput onQuery={handleQuery} isLoading={isLoading} />
            </div>
          </div>

          {/* Right Panel - Results */}
          <div className="lg:col-span-8">
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 backdrop-blur-sm min-h-[600px]">
              {error && (
                <div className="mb-4 bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                  <p className="text-red-400 text-sm">{error}</p>
                </div>
              )}

              <ResultsPanel
                results={queryResults?.sources || []}
                answer={queryResults?.answer || ''}
                metadata={queryResults?.metadata}
                isLoading={isLoading}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700/50 mt-12 py-6">
        <div className="container mx-auto px-6 text-center text-sm text-slate-500">
          <p>Copyright © 2025 Samay Mehar. All Rights Reserved.</p>
          <p className="mt-1">VectorMind - Proprietary Software | Patent Pending</p>
        </div>
      </footer>
    </div>
  );
}
