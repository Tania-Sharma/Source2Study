import React, { useState, useRef } from 'react';
import { api } from '../api';

export default function UploadPage({ onRefreshData, showToast, setActiveTab }) {
  const [uploadMode, setUploadMode] = useState('papers'); // 'papers' or 'resources'
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [webUrl, setWebUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

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
    const validExtensions = uploadMode === 'papers'
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
      if (uploadMode === 'papers') {
        const result = await api.uploadPapers(selectedFiles);
        showToast(`Extracted questions from ${selectedFiles.length} paper(s)!`, 'success');
        setSelectedFiles([]);
        onRefreshData();
        if (result.potential_duplicates && result.potential_duplicates.length > 0) {
          setActiveTab('duplicates');
        } else {
          setActiveTab('bank');
        }
      } else {
        await api.uploadResources(selectedFiles);
        showToast(`Indexed ${selectedFiles.length} resource(s) into RAG knowledge base!`, 'success');
        setSelectedFiles([]);
        onRefreshData();
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
      showToast('YouTube transcript extracted and indexed!', 'success');
      setYoutubeUrl('');
      onRefreshData();
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
      showToast('Web article extracted and indexed!', 'success');
      setWebUrl('');
      onRefreshData();
    } catch (err) {
      showToast(`Web error: ${err.message}`, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div>
      <div className="section-header">
        <h1 className="section-title">
          <span>📁</span> Upload Learning Resources & Question Papers
        </h1>
        <p className="section-subtitle">
          Select files or links to process with text extraction, OCR fallback, and duplicate detection.
        </p>
      </div>

      {/* Mode Selector */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <button
          className={`btn ${uploadMode === 'papers' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => {
            setUploadMode('papers');
            setSelectedFiles([]);
          }}
        >
          📄 Question Papers (Unified Bank & Deduplication)
        </button>
        <button
          className={`btn ${uploadMode === 'resources' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => {
            setUploadMode('resources');
            setSelectedFiles([]);
          }}
        >
          🧠 Study Resources (PDF, DOCX, Images, YouTube, Web)
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
          accept={uploadMode === 'papers' ? '.pdf,.docx,.txt,.md' : '.pdf,.docx,.png,.jpg,.jpeg,.webp'}
          onChange={handleFileSelect}
        />
        <div className="dropzone-icon">📥</div>
        <div className="dropzone-title">
          Drag & Drop {uploadMode === 'papers' ? 'Question Papers' : 'Study Files'} Here
        </div>
        <div className="dropzone-text">
          or click to browse from your computer ({uploadMode === 'papers' ? 'PDF, DOCX, TXT' : 'PDF, DOCX, Images'})
        </div>
      </div>

      {/* Selected Files List */}
      {selectedFiles.length > 0 && (
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 600 }}>Selected Files ({selectedFiles.length})</h4>
            <button className="btn btn-sm btn-danger" onClick={() => setSelectedFiles([])}>
              Clear All
            </button>
          </div>

          <div className="file-queue">
            {selectedFiles.map((file, idx) => (
              <div key={idx} className="file-item">
                <div className="file-info">
                  <span className="file-icon">📄</span>
                  <div>
                    <div className="file-name">{file.name}</div>
                    <div className="file-size">{(file.size / 1024).toFixed(1)} KB</div>
                  </div>
                </div>
                <button
                  className="btn btn-sm btn-secondary"
                  style={{ color: 'var(--danger)', padding: '0.2rem 0.5rem' }}
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(idx);
                  }}
                >
                  ✕ Remove
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
            {isProcessing ? '⏳ Extracting & Processing...' : `Process & Extract ${selectedFiles.length} File(s)`}
          </button>
        </div>
      )}

      {/* Web and YouTube URL input for Study Resources mode */}
      {uploadMode === 'resources' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '2rem' }}>
          {/* YouTube Card */}
          <div className="card">
            <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>▶️</span> Add YouTube Video
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem' }}>
              Fetches full timestamps and transcript segments for conversational RAG.
            </p>
            <form onSubmit={handleAddYoutube} style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                className="search-input"
                style={{ flex: 1 }}
                placeholder="https://youtube.com/watch?v=..."
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
              />
              <button type="submit" className="btn btn-primary" disabled={isProcessing || !youtubeUrl.trim()}>
                Index Video
              </button>
            </form>
          </div>

          {/* Web Card */}
          <div className="card">
            <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>🌐</span> Add Website / Article URL
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem' }}>
              Safely extracts article text, headings, and tables, stripping boilerplate.
            </p>
            <form onSubmit={handleAddWeb} style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                className="search-input"
                style={{ flex: 1 }}
                placeholder="https://example.com/topic..."
                value={webUrl}
                onChange={(e) => setWebUrl(e.target.value)}
              />
              <button type="submit" className="btn btn-primary" disabled={isProcessing || !webUrl.trim()}>
                Index Web
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
