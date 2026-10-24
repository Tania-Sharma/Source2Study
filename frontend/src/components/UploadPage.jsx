import React, { useState, useEffect, useRef } from 'react';
import {
  FolderUp,
  FileText,
  Globe,
  Trash2,
  ExternalLink,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  BookOpen,
  BrainCircuit,
  X,
  UploadCloud,
} from 'lucide-react';
import { api } from '../api';

export default function UploadPage({
  onRefreshData,
  showToast,
  setActiveTab,
  onSelectResourceForStudy,
}) {
  const [activeTabMode, setActiveTabMode] = useState('resources'); // 'resources' | 'papers'
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [webUrl, setWebUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  // Resource List
  const [resources, setResources] = useState([]);
  const [loadingResources, setLoadingResources] = useState(false);
  const [resourceToDelete, setResourceToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fileInputRef = useRef(null);

  useEffect(() => {
    loadResources();
  }, []);

  const loadResources = async () => {
    setLoadingResources(true);
    try {
      const data = await api.listResources();
      setResources(data || []);
    } catch (err) {
      console.warn('Failed to fetch resources:', err);
    } finally {
      setLoadingResources(false);
    }
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files || []);
    addFiles(files);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files || []);
    addFiles(files);
  };

  const addFiles = (files) => {
    const validExtensions =
      activeTabMode === 'papers'
        ? ['.pdf', '.docx', '.txt', '.md']
        : ['.pdf', '.docx', '.png', '.jpg', '.jpeg', '.webp'];

    const filtered = files.filter((f) => {
      const ext = '.' + f.name.split('.').pop().toLowerCase();
      return validExtensions.includes(ext);
    });

    if (filtered.length < files.length) {
      showToast('Some unsupported files were skipped.', 'error');
    }

    setSelectedFiles((prev) => [...prev, ...filtered]);
  };

  const removeFile = (index) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleProcessUpload = async () => {
    if (selectedFiles.length === 0) {
      showToast('Please select at least one file.', 'error');
      return;
    }

    setIsProcessing(true);
    try {
      if (activeTabMode === 'papers') {
        const result = await api.uploadPapers(selectedFiles);
        showToast(`Extracted questions from ${selectedFiles.length} paper(s)!`, 'success');
        setSelectedFiles([]);
        if (onRefreshData) onRefreshData();
        if (result.potential_duplicates && result.potential_duplicates.length > 0) {
          setActiveTab('duplicates');
        } else {
          setActiveTab('bank');
        }
      } else {
        const res = await api.uploadResources(selectedFiles);
        const count = res.processed?.length || selectedFiles.length;
        showToast(`Indexed ${count} resource(s) into AI Knowledge Base!`, 'success');
        setSelectedFiles([]);
        loadResources();
        if (onRefreshData) onRefreshData();
      }
    } catch (err) {
      showToast(`Upload failed: ${err.message}`, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAddYoutube = async (e) => {
    e.preventDefault();
    if (!youtubeUrl.trim()) return;
    setIsProcessing(true);
    try {
      await api.addYoutube(youtubeUrl);
      showToast('YouTube transcript extracted and indexed into knowledge base!', 'success');
      setYoutubeUrl('');
      loadResources();
      if (onRefreshData) onRefreshData();
    } catch (err) {
      showToast(`YouTube error: ${err.message}`, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAddWeb = async (e) => {
    e.preventDefault();
    if (!webUrl.trim()) return;
    setIsProcessing(true);
    try {
      await api.addWeb(webUrl);
      showToast('Web article content extracted and indexed!', 'success');
      setWebUrl('');
      loadResources();
      if (onRefreshData) onRefreshData();
    } catch (err) {
      showToast(`Web error: ${err.message}`, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDeleteResource = async () => {
    if (!resourceToDelete) return;
    setIsDeleting(true);
    try {
      await api.deleteResource(resourceToDelete.id);
      showToast('Resource deleted successfully.', 'success');
      setResourceToDelete(null);
      loadResources();
      if (onRefreshData) onRefreshData();
    } catch (err) {
      showToast(`Delete failed: ${err.message}`, 'error');
    } finally {
      setIsDeleting(false);
    }
  };

  const getFormatBadge = (type) => {
    switch (type?.toLowerCase()) {
      case 'youtube':
        return (
          <span className="badge badge-danger">
            <Youtube size={12} /> YouTube
          </span>
        );
      case 'website':
      case 'web':
        return (
          <span className="badge badge-success">
            <Globe size={12} /> Website
          </span>
        );
      case 'docx':
        return (
          <span className="badge badge-info">
            <FileText size={12} /> DOCX
          </span>
        );
      default:
        return (
          <span className="badge badge-primary">
            <FileText size={12} /> PDF
          </span>
        );
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="section-header">
        <h1 className="section-title">
          <FolderUp size={28} style={{ color: '#818cf8' }} />
          <span>Resource Ingestion & Management</span>
        </h1>
        <p className="section-subtitle">
          Upload course notes, textbook PDFs, lecture videos, or exam papers. All materials are parsed, chunked, and indexed for grounded AI learning.
        </p>
      </div>

      {/* Mode Selector Tabs */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.75rem' }}>
        <button
          className={`btn ${activeTabMode === 'resources' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => {
            setActiveTabMode('resources');
            setSelectedFiles([]);
          }}
        >
          <BrainCircuit size={16} />
          <span>AI Study Materials (PDF, DOCX, Video, Web)</span>
        </button>

        <button
          className={`btn ${activeTabMode === 'papers' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => {
            setActiveTabMode('papers');
            setSelectedFiles([]);
          }}
        >
          <BookOpen size={16} />
          <span>Exam Papers (Question Bank & Deduplication)</span>
        </button>
      </div>

      {/* Dropzone */}
      <div
        className={`dropzone ${isDragging ? 'active' : ''}`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current && fileInputRef.current.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          multiple
          accept={
            activeTabMode === 'papers'
              ? '.pdf,.docx,.txt,.md'
              : '.pdf,.docx,.png,.jpg,.jpeg,.webp'
          }
          onChange={handleFileSelect}
        />
        <div className="dropzone-icon">
          <UploadCloud size={48} />
        </div>
        <div className="dropzone-title">
          Drag & Drop {activeTabMode === 'papers' ? 'Exam Papers' : 'Course Materials'} Here
        </div>
        <div className="dropzone-text">
          or click to browse from your device ({activeTabMode === 'papers' ? 'PDF, DOCX, TXT' : 'PDF, DOCX, Images with OCR fallback'})
        </div>
      </div>

      {/* Selected Files Queue */}
      {selectedFiles.length > 0 && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 600 }}>
              Files Ready for Ingestion ({selectedFiles.length})
            </h4>
            <button className="btn btn-sm btn-outline" onClick={() => setSelectedFiles([])}>
              Clear Queue
            </button>
          </div>

          <div className="file-queue">
            {selectedFiles.map((file, idx) => (
              <div key={idx} className="file-item">
                <div className="file-info">
                  <FileText size={18} style={{ color: '#818cf8' }} />
                  <div>
                    <div className="file-name">{file.name}</div>
                    <div className="file-size">{(file.size / 1024).toFixed(1)} KB</div>
                  </div>
                </div>
                <button
                  className="btn btn-sm btn-danger btn-icon"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(idx);
                  }}
                  title="Remove file"
                >
                  <X size={15} />
                </button>
              </div>
            ))}
          </div>

          <button
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.85rem' }}
            disabled={isProcessing}
            onClick={handleProcessUpload}
          >
            {isProcessing ? (
              <>
                <RefreshCw size={16} className="spin-animation" />
                <span>Extracting & Indexing Materials...</span>
              </>
            ) : (
              <>
                <UploadCloud size={16} />
                <span>Process & Index {selectedFiles.length} File(s)</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Web & YouTube URL Ingest (For Study Materials mode) */}
      {activeTabMode === 'resources' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
          {/* YouTube Video Ingest */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Youtube size={22} style={{ color: '#f43f5e' }} />
              <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Index YouTube Lecture</h3>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
              Extracts automated or manual subtitles with time-aligned chunks for conversational learning.
            </p>
            <form onSubmit={handleAddYoutube} style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                className="input-text"
                style={{ flex: 1 }}
                placeholder="https://www.youtube.com/watch?v=..."
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
              />
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isProcessing || !youtubeUrl.trim()}
              >
                {isProcessing ? 'Processing...' : 'Index Video'}
              </button>
            </form>
          </div>

          {/* Web Article Ingest */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Globe size={22} style={{ color: '#10b981' }} />
              <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Index Website or Article</h3>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
              Extracts clean article text, headings, and tables, stripping boilerplate ads and navigation.
            </p>
            <form onSubmit={handleAddWeb} style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                className="input-text"
                style={{ flex: 1 }}
                placeholder="https://example.com/lecture-notes..."
                value={webUrl}
                onChange={(e) => setWebUrl(e.target.value)}
              />
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isProcessing || !webUrl.trim()}
              >
                {isProcessing ? 'Processing...' : 'Index Web'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Existing Uploaded Resources Management Table */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>
              Available Learning Resources ({resources.length})
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Materials currently indexed in your local vector store and ready for AI learning.
            </p>
          </div>
          <button className="btn btn-sm btn-outline" onClick={loadResources}>
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>
        </div>

        {loadingResources ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            Loading indexed resources...
          </div>
        ) : resources.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="resource-table">
              <thead>
                <tr>
                  <th>Format</th>
                  <th>Source Name / URL</th>
                  <th>Date Added</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {resources.map((r) => (
                  <tr key={r.id}>
                    <td>{getFormatBadge(r.source_type)}</td>
                    <td>
                      <div style={{ fontWeight: 500, color: 'var(--text-primary)' }}>
                        {r.source_name}
                      </div>
                      {r.url && (
                        <a
                          href={r.url}
                          target="_blank"
                          rel="noreferrer"
                          style={{ fontSize: '0.78rem', color: '#818cf8', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.25rem', marginTop: '0.2rem' }}
                        >
                          <span style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {r.url}
                          </span>
                          <ExternalLink size={11} />
                        </a>
                      )}
                    </td>
                    <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                      {r.created_at ? new Date(r.created_at).toLocaleDateString() : 'Recent'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => {
                            if (onSelectResourceForStudy) {
                              onSelectResourceForStudy(r.id);
                            }
                            setActiveTab('assistant');
                          }}
                          title="Open in AI Workspace"
                        >
                          <BrainCircuit size={14} />
                          <span>Study</span>
                        </button>
                        <button
                          className="btn btn-sm btn-danger btn-icon"
                          onClick={() => setResourceToDelete(r)}
                          title="Delete Resource"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
            <FolderUp size={38} style={{ opacity: 0.4, marginBottom: '0.75rem' }} />
            <div style={{ fontWeight: 500, color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
              No indexed resources yet
            </div>
            <p style={{ fontSize: '0.85rem' }}>
              Drop your first PDF, Word DOCX, or paste a YouTube/Web URL above to start.
            </p>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {resourceToDelete && (
        <div className="modal-overlay" onClick={() => !isDeleting && setResourceToDelete(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', color: 'var(--danger)' }}>
              <AlertCircle size={24} />
              <h3 style={{ fontSize: '1.2rem', fontWeight: 600 }}>Delete Learning Resource?</h3>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: 1.6 }}>
              Are you sure you want to delete <strong style={{ color: 'var(--text-primary)' }}>{resourceToDelete.source_name}</strong>? This will remove the document from your knowledge base and database.
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button
                className="btn btn-secondary"
                disabled={isDeleting}
                onClick={() => setResourceToDelete(null)}
              >
                Cancel
              </button>
              <button
                className="btn btn-danger"
                disabled={isDeleting}
                onClick={handleDeleteResource}
              >
                {isDeleting ? 'Deleting...' : 'Delete Resource'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
