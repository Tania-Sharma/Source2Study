import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function QuestionBankView({ papers, onSelectQuestionForAI, showToast }) {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPaper, setSelectedPaper] = useState('');
  const [expandedOccurrences, setExpandedOccurrences] = useState({});

  const loadQuestions = async () => {
    setLoading(true);
    try {
      const res = await api.getQuestionBank({
        status: 'unique',
        search: searchTerm,
        paper: selectedPaper,
      });
      setQuestions(res.questions || []);
    } catch (err) {
      showToast(`Error loading questions: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      loadQuestions();
    }, 250);
    return () => clearTimeout(timer);
  }, [searchTerm, selectedPaper]);

  const toggleOccurrences = (id) => {
    setExpandedOccurrences((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  return (
    <div>
      <div className="section-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 className="section-title">
              <span>📚</span> Consolidated Question Bank
            </h1>
            <p className="section-subtitle">
              Browse, filter, and export the unified collection of deduplicated questions across all papers.
            </p>
          </div>

          {/* Export Dropdown / Buttons */}
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <a
              href={api.getExportUrl('csv')}
              target="_blank"
              rel="noreferrer"
              className="btn btn-sm btn-secondary"
              download="question_bank.csv"
            >
              📊 Export CSV
            </a>
            <a
              href={api.getExportUrl('excel')}
              target="_blank"
              rel="noreferrer"
              className="btn btn-sm btn-secondary"
              download="question_bank.xlsx"
            >
              📑 Export Excel
            </a>
            <a
              href={api.getExportUrl('pdf')}
              target="_blank"
              rel="noreferrer"
              className="btn btn-sm btn-primary"
              download="question_bank.pdf"
            >
              📄 Export PDF
            </a>
          </div>
        </div>
      </div>

      {/* Toolbar: Search and Filter */}
      <div className="card toolbar">
        <div style={{ display: 'flex', gap: '1rem', flex: 1, flexWrap: 'wrap' }}>
          <input
            type="text"
            className="search-input"
            style={{ flex: 1 }}
            placeholder="Search questions by keyword..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />

          <select
            className="select-input"
            value={selectedPaper}
            onChange={(e) => setSelectedPaper(e.target.value)}
          >
            <option value="">All Question Papers</option>
            {papers.map((p) => (
              <option key={p.id} value={p.filename}>
                {p.filename}
              </option>
            ))}
          </select>
        </div>

        <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Showing <strong>{questions.length}</strong> unique questions
        </div>
      </div>

      {/* Questions List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          Loading questions...
        </div>
      ) : questions.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
          <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>🔍</div>
          <h3>No Questions Found</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Try adjusting your search filters or upload question papers.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {questions.map((q, idx) => {
            const isExpanded = !!expandedOccurrences[q.id];
            return (
              <div key={q.id} className="question-item">
                <div className="question-header">
                  <div style={{ display: 'flex', gap: '0.75rem' }}>
                    <span style={{ color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.9rem', minWidth: '24px' }}>
                      {idx + 1}.
                    </span>
                    <div className="question-text">{q.canonical_text}</div>
                  </div>

                  {/* AI Quick Actions */}
                  <div style={{ display: 'flex', gap: '0.4rem', flexShrink: 0 }}>
                    <button
                      className="btn btn-sm btn-secondary"
                      style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                      title="Explain this question simply"
                      onClick={() => onSelectQuestionForAI(q.canonical_text, 'explain')}
                    >
                      💡 Explain
                    </button>
                    <button
                      className="btn btn-sm btn-secondary"
                      style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                      title="Ask AI study question"
                      onClick={() => onSelectQuestionForAI(q.canonical_text, 'ask')}
                    >
                      ✨ Ask AI
                    </button>
                  </div>
                </div>

                <div className="question-meta">
                  {q.marks && <span className="badge badge-info">{q.marks}</span>}
                  {q.section && <span className="badge badge-warning">{q.section}</span>}
                  {q.topic && <span className="badge badge-ai">{q.topic}</span>}

                  <button
                    onClick={() => toggleOccurrences(q.id)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--primary)',
                      cursor: 'pointer',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      marginLeft: 'auto',
                    }}
                  >
                    🔁 Appears in {q.occurrences_count} paper{q.occurrences_count > 1 ? 's' : ''} {isExpanded ? '▲' : '▼'}
                  </button>
                </div>

                {/* Expandable Occurrences */}
                {isExpanded && (
                  <div className="occurrences-box">
                    <div style={{ fontWeight: 600, marginBottom: '0.4rem', color: 'var(--text-primary)' }}>
                      Occurrences in Source Papers:
                    </div>
                    {q.occurrences.map((occ, oIdx) => (
                      <div key={oIdx} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.2rem 0' }}>
                        <span>
                          <strong>{occ.paper_name}</strong> {occ.original_number ? `— ${occ.original_number}` : ''}
                        </span>
                        <span style={{ color: 'var(--text-muted)' }}>{occ.marks || ''}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
