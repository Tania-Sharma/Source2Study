import React from 'react';

export default function Dashboard({ stats, papers, setActiveTab }) {
  return (
    <div>
      <div className="section-header" style={{ marginBottom: '2.5rem' }}>
        <h1 className="section-title">
          <span>👋</span> Welcome to Source2Study
        </h1>
        <p className="section-subtitle">
          AI-powered study assistant with automatic question extraction, duplicate detection, and unified question banking.
        </p>
      </div>

      {/* Metric Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-title">Exam Papers Processed</span>
            <span className="stat-icon">📄</span>
          </div>
          <div className="stat-value">{stats.total_papers || 0}</div>
          <span className="stat-subtext">PDFs & DOCX files analyzed</span>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-title">Total Questions Extracted</span>
            <span className="stat-icon">📝</span>
          </div>
          <div className="stat-value">{stats.total_extracted_questions || 0}</div>
          <span className="stat-subtext">Across all question papers</span>
        </div>

        <div className="stat-card" style={{ borderColor: 'rgba(16, 185, 129, 0.4)' }}>
          <div className="stat-header">
            <span className="stat-title">Unique Questions</span>
            <span className="stat-icon">🎯</span>
          </div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>
            {stats.unique_questions || 0}
          </div>
          <span className="stat-subtext">Ready for student practice</span>
        </div>

        <div className="stat-card" style={{ borderColor: 'rgba(245, 158, 11, 0.4)' }}>
          <div className="stat-header">
            <span className="stat-title">Duplicates Detected</span>
            <span className="stat-icon">🔁</span>
          </div>
          <div className="stat-value" style={{ color: 'var(--warning)' }}>
            {(stats.exact_duplicates || 0) + (stats.semantic_duplicates || 0)}
          </div>
          <span className="stat-subtext">
            {stats.exact_duplicates || 0} exact &bull; {stats.semantic_duplicates || 0} semantic
          </span>
        </div>
      </div>

      {/* Quick Action Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>🚀</span> Upload Previous-Year Papers
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
              Drop multiple question papers to extract questions, deduplicate repeated questions automatically, and generate a master question bank.
            </p>
          </div>
          <div>
            <button className="btn btn-primary" onClick={() => setActiveTab('upload')}>
              Upload Papers &rarr;
            </button>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>✨</span> Ask AI & Take Quizzes
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
              Use our RAG-grounded AI assistant to get simple explanations, generate quizzes, or ask deep questions grounded exclusively in your documents.
            </p>
          </div>
          <div>
            <button className="btn btn-secondary" onClick={() => setActiveTab('assistant')}>
              Open Assistant &rarr;
            </button>
          </div>
        </div>
      </div>

      {/* Processed Papers Table */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Recent Question Papers</h3>
          <button className="btn btn-sm btn-secondary" onClick={() => setActiveTab('bank')}>
            View All Questions
          </button>
        </div>

        {papers && papers.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {papers.map((p) => (
              <div
                key={p.id}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.75rem 1rem',
                  background: 'rgba(15, 23, 42, 0.4)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border)',
                }}
              >
                <div>
                  <div style={{ fontWeight: 500, fontSize: '0.95rem' }}>{p.title || p.filename}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Type: {p.file_type.toUpperCase()} &bull; Uploaded: {new Date(p.uploaded_at).toLocaleDateString()}
                  </div>
                </div>
                <div>
                  <span className="badge badge-info">{p.extracted_count} questions</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)' }}>
            No question papers uploaded yet. Click "Upload Papers" to get started!
          </div>
        )}
      </div>
    </div>
  );
}
