/**
 * Upload Section Component
 * 
 * Copyright © 2025 Samay Mehar. All Rights Reserved.
 * PROPRIETARY SOFTWARE - PATENT PENDING
 */

'use client';

import { useState, useCallback, useRef } from 'react';
import { Upload, X, FileText, Image, File, CheckCircle2, AlertCircle } from 'lucide-react';
import { uploadFile, formatFileSize, getFileExtension, getFileTypeCategory } from '@/lib/api';

interface UploadedFile {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  response?: any;
  error?: string;
}

export function UploadSection() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      addFiles(selectedFiles);
    }
  }, []);

  const addFiles = (newFiles: File[]) => {
    const uploadedFiles: UploadedFile[] = newFiles.map((file) => ({
      id: `${Date.now()}-${Math.random()}`,
      file,
      status: 'pending',
      progress: 0,
    }));
    setFiles((prev) => [...prev, ...uploadedFiles]);
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const uploadFiles = async () => {
    const pendingFiles = files.filter((f) => f.status === 'pending' || f.status === 'error');

    for (const uploadedFile of pendingFiles) {
      setFiles((prev) =>
        prev.map((f) =>
          f.id === uploadedFile.id ? { ...f, status: 'uploading', progress: 50 } : f
        )
      );

      try {
        const response = await uploadFile(uploadedFile.file);
        setFiles((prev) =>
          prev.map((f) =>
            f.id === uploadedFile.id
              ? { ...f, status: 'success', progress: 100, response }
              : f
          )
        );
      } catch (error) {
        setFiles((prev) =>
          prev.map((f) =>
            f.id === uploadedFile.id
              ? {
                  ...f,
                  status: 'error',
                  progress: 0,
                  error: error instanceof Error ? error.message : 'Upload failed',
                }
              : f
          )
        );
      }
    }
  };

  const getFileIcon = (filename: string) => {
    const ext = getFileExtension(filename);
    const category = getFileTypeCategory(ext);

    switch (category) {
      case 'image':
        return <Image className="h-5 w-5 text-purple-400" />;
      case 'document':
      case 'spreadsheet':
        return <FileText className="h-5 w-5 text-blue-400" />;
      default:
        return <File className="h-5 w-5 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-100">Upload Documents</h2>
        <span className="text-sm text-slate-400">{files.length} file(s)</span>
      </div>

      {/* Drag-drop area */}
      <div
        className={`
          border-2 border-dashed rounded-lg p-8 transition-all cursor-pointer
          ${
            dragActive
              ? 'border-cyan-500 bg-cyan-500/10'
              : 'border-slate-700 bg-slate-800/50 hover:border-cyan-500/50'
          }
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={handleFileInput}
          accept=".txt,.pdf,.png,.jpg,.jpeg,.docx,.xlsx,.csv,.md"
        />
        <div className="flex flex-col items-center justify-center space-y-3">
          <Upload className="h-12 w-12 text-slate-500" />
          <div className="text-center">
            <p className="text-slate-300 font-medium">Drag files here or click to upload</p>
            <p className="text-sm text-slate-500 mt-1">
              Supports: PDF, DOCX, XLSX, CSV, TXT, PNG, JPG
            </p>
          </div>
        </div>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-2 max-h-[40vh] overflow-y-auto">
          {files.map((uploadedFile) => (
            <div
              key={uploadedFile.id}
              className="bg-slate-800 border border-slate-700 rounded-lg p-3 flex items-center justify-between"
            >
              <div className="flex items-center space-x-3 flex-1 min-w-0">
                {getFileIcon(uploadedFile.file.name)}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-200 truncate">
                    {uploadedFile.file.name}
                  </p>
                  <div className="flex items-center space-x-2 text-xs text-slate-500">
                    <span>{formatFileSize(uploadedFile.file.size)}</span>
                    <span>•</span>
                    <span className="uppercase">{getFileExtension(uploadedFile.file.name)}</span>
                  </div>
                  {uploadedFile.error && (
                    <p className="text-xs text-red-400 mt-1">{uploadedFile.error}</p>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-2">
                {uploadedFile.status === 'success' && (
                  <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                )}
                {uploadedFile.status === 'error' && (
                  <AlertCircle className="h-5 w-5 text-red-500" />
                )}
                {uploadedFile.status === 'uploading' && (
                  <div className="h-5 w-5 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
                )}
                <button
                  onClick={() => removeFile(uploadedFile.id)}
                  className="text-slate-500 hover:text-slate-300 transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload button */}
      {files.some((f) => f.status === 'pending' || f.status === 'error') && (
        <button
          onClick={uploadFiles}
          className="w-full bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg transition-colors font-medium"
        >
          Upload {files.filter((f) => f.status === 'pending' || f.status === 'error').length} File(s)
        </button>
      )}
    </div>
  );
}
