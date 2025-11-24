/**
 * Query Input Component
 * 
 * Copyright © 2025 Samay Mehar. All Rights Reserved.
 * PROPRIETARY SOFTWARE - PATENT PENDING
 */

'use client';

import { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

interface QueryInputProps {
  onQuery: (query: string, queryType: string) => void;
  isLoading: boolean;
}

const QUERY_TYPES = [
  { id: 'factual', label: 'Factual', description: 'Direct answers from documents' },
  { id: 'exploratory', label: 'Exploratory', description: 'Discover related information' },
  { id: 'cross-modal', label: 'Cross-Modal', description: 'Search across text and images' },
];

export function QueryInput({ onQuery, isLoading }: QueryInputProps) {
  const [queryText, setQueryText] = useState('');
  const [selectedType, setSelectedType] = useState('factual');

  const handleSubmit = () => {
    if (queryText.trim() && !isLoading) {
      onQuery(queryText, selectedType);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-slate-100">Query Documents</h3>

      {/* Query type selector */}
      <div className="space-y-2">
        <label className="text-sm text-slate-400">Query Type</label>
        <div className="flex gap-2 flex-wrap">
          {QUERY_TYPES.map((type) => (
            <button
              key={type.id}
              onClick={() => setSelectedType(type.id)}
              className={`
                px-3 py-2 text-sm rounded-lg transition-all
                ${
                  selectedType === type.id
                    ? 'bg-cyan-600 text-white'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }
              `}
            >
              {type.label}
            </button>
          ))}
        </div>
        <p className="text-xs text-slate-500">
          {QUERY_TYPES.find((t) => t.id === selectedType)?.description}
        </p>
      </div>

      {/* Query textarea */}
      <div className="space-y-2">
        <label className="text-sm text-slate-400">Your Question</label>
        <textarea
          value={queryText}
          onChange={(e) => setQueryText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question or describe what you're looking for..."
          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-slate-100
                   placeholder:text-slate-500 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500
                   transition-colors resize-none"
          rows={4}
          disabled={isLoading}
        />
        <p className="text-xs text-slate-500">
          Press Enter to search, Shift+Enter for new line
        </p>
      </div>

      {/* Search button */}
      <button
        onClick={handleSubmit}
        disabled={!queryText.trim() || isLoading}
        className="w-full bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-700 disabled:cursor-not-allowed
                 text-white px-4 py-3 rounded-lg transition-colors font-medium flex items-center justify-center space-x-2"
      >
        {isLoading ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Searching...</span>
          </>
        ) : (
          <>
            <Search className="h-5 w-5" />
            <span>Search</span>
          </>
        )}
      </button>
    </div>
  );
}
