/**
 * Results Panel Component
 * 
 * Copyright © 2025 Samay Mehar. All Rights Reserved.
 * PROPRIETARY SOFTWARE - PATENT PENDING
 */

'use client';

import { FileText, Image, File, Clock, Database } from 'lucide-react';
import { Source } from '@/lib/api';
import { formatDate, calculateRelevance, getFileExtension } from '@/lib/api';

interface ResultsPanelProps {
  results: Source[];
  answer: string;
  metadata?: {
    intent?: string;
    provider?: string;
    query_type?: string;
    processing_time?: number;
  };
  isLoading: boolean;
}

export function ResultsPanel({ results, answer, metadata, isLoading }: ResultsPanelProps) {
  const getSourceIcon = (filename?: string) => {
    if (!filename) return <File className="h-5 w-5 text-slate-400" />;

    const ext = getFileExtension(filename);
    if (['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(ext)) {
      return <Image className="h-5 w-5 text-purple-400" />;
    }
    return <FileText className="h-5 w-5 text-blue-400" />;
  };

  const getFileTypeBadge = (filename?: string) => {
    if (!filename) return 'Unknown';
    const ext = getFileExtension(filename).toUpperCase();
    return ext || 'FILE';
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-slate-100">Results</h2>
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center space-y-4">
            <div className="h-12 w-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-slate-400">Searching documents...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return (
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-slate-100">Results</h2>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-12 text-center">
          <Database className="h-16 w-16 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400 text-lg">No results yet</p>
          <p className="text-slate-500 text-sm mt-2">
            Upload documents and run a query to see results
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-100">Results</h2>
        <div className="flex items-center space-x-4 text-sm">
          {metadata?.processing_time && (
            <div className="flex items-center space-x-1 text-slate-400">
              <Clock className="h-4 w-4" />
              <span>{metadata.processing_time}ms</span>
            </div>
          )}
          <span className="text-slate-400">{results.length} result(s)</span>
        </div>
      </div>

      {/* Answer summary */}
      {answer && (
        <div className="bg-gradient-to-br from-cyan-900/20 to-emerald-900/20 border border-cyan-500/30 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <div className="h-2 w-2 bg-emerald-500 rounded-full animate-pulse-slow" />
            <h3 className="text-sm font-semibold text-cyan-400">Answer</h3>
          </div>
          <p className="text-slate-200 leading-relaxed">{answer}</p>
          {metadata && (
            <div className="mt-3 pt-3 border-t border-slate-700 flex items-center space-x-4 text-xs text-slate-500">
              {metadata.provider && <span>Provider: {metadata.provider}</span>}
              {metadata.intent && <span>Intent: {metadata.intent}</span>}
            </div>
          )}
        </div>
      )}

      {/* Results list */}
      <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-slate-900">
        {results.map((result, index) => {
          const relevance = result.score ? calculateRelevance(result.score) : 0;

          return (
            <div
              key={`${result.document_id}-${index}`}
              className="bg-slate-800/70 border border-slate-700 rounded-lg p-4 hover:border-slate-600
                       transition-all cursor-pointer group"
            >
              {/* Header */}
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center space-x-2 flex-1 min-w-0">
                  {getSourceIcon(result.filename)}
                  <h4 className="font-medium text-slate-100 truncate">
                    {result.filename || `Source ${index + 1}`}
                  </h4>
                </div>
                <span className="text-xs px-2 py-1 rounded bg-slate-700 text-slate-300 whitespace-nowrap ml-2">
                  {getFileTypeBadge(result.filename)}
                </span>
              </div>

              {/* Relevance score */}
              <div className="mb-3">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">Relevance</span>
                  <span className="text-emerald-400 font-medium">{relevance}%</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-1.5">
                  <div
                    className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-1.5 rounded-full transition-all duration-500"
                    style={{ width: `${relevance}%` }}
                  />
                </div>
              </div>

              {/* Content preview */}
              <p className="text-sm text-slate-300 leading-relaxed line-clamp-3 mb-3">
                {result.text || 'No preview available'}
              </p>

              {/* Metadata footer */}
              {result.metadata && (
                <div className="pt-3 border-t border-slate-700/50 flex items-center justify-between text-xs text-slate-500">
                  <span>Document ID: {result.document_id?.slice(0, 8)}...</span>
                  {result.metadata.chunk_index !== undefined && (
                    <span>Chunk: {result.metadata.chunk_index + 1}</span>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
