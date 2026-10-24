import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Download,
  Search,
  FileSpreadsheet,
  FileText,
  Lightbulb,
  BrainCircuit,
  Award,
  ChevronDown,
  ChevronUp,
  Layers,
} from 'lucide-react';
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
      {/* Header */}
      <div className="section-header">
        <div className="section-header-row">
          <div>
            <h1 className="section-title">
              <BookOpen size={28} style={{ color: '#818cf8' }} />
              <span>Consolidated Question Bank</span>
            </h1>
            <p className="section-subtitle">
              Browse, search, and export the deduplicated master bank of questions extracted across all exam papers.
            </p>
          </div>

          {/* Export Buttons */}
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <a
              href={api.getExportUrl('csv')}
              target="_blank"
              rel="noreferrer"
              className="btn btn-sm btn-secondary"
              download="question_bank.csv"
            >
              <Download size={14} />
              <span>Export CSV</span>
            </a>
            <a
              href={api.getExportUrl('excel')}
              target="_blank"
              rel="noreferrer"
              className="btn btn-sm btn-secondary"
              download="question_bank.xlsx"
            >
              <FileSpreadsheet size={14} style={{ color: '#10b981' }} />
              <span>Export Excel</span>
            </a>
            <a
              href={api.getExportUrl('pdf')}
              target="_blank"
              rel="noreferrer"
              className="btn btn-sm btn-primary"
              download="question_bank.pdf"
            >
              <FileText size={14} />
              <span>Export PDF</span>
            </a>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1rem 1.25rem' }}>
        <div style={{ display: 'flex', gap: '1rem', flex: 1, flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: '0.75rem', flex: 1, minWidth: '280px' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <input
                type="text"
                className="input-text"
                style={{ paddingLeft: '2.25rem' }}
                placeholder="Search questions by keyword..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <Search
                size={16}
                style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}
              />
            </div>

            <select
              className="select-input"
              style={{ width: 'auto', minWidth: '200px' }}
              value={selectedPaper}
              onChange={(e) => setSelectedPaper(e.target.value)}
            >
              <option value="">All Question Papers</option>
              {papers.map((p) => (
                <option key={p.id} value={p.filename}>
                  {p.title || p.filename}
                </option>
              ))}
            </select>
          </div>

          <div style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
            Showing <strong>{questions.length}</strong> unique questions
          </div>
        </div>
      </div>

      {/* Questions List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          Loading question bank...
        </div>
      ) : questions.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
          <Search size={36} style={{ color: 'var(--text-muted)', marginBottom: '0.75rem', opacity: 0.5 }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            No Questions Found
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem' }}>
            Try adjusting your search filters or upload past question papers in the Upload tab.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {questions.map((q, idx) => {
            const isExpanded = !!expandedOccurrences[q.id];
            return (
              <div
                key={q.id}
                className="card"
                style={{ padding: '1.25rem', transition: 'all 0.15s ease' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
                  <div style={{ display: 'flex', gap: '0.75rem', flex: 1, minWidth: '280px' }}>
                    <span style={{ color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.9rem', minWidth: '24px' }}>
                      {idx + 1}.
                    </span>
                    <div style={{ fontSize: '0.95rem', fontWeight: 500, color: 'var(--text-primary)', lineHeight: 1.5 }}>
                      {q.canonical_text}
                    </div>
                  </div>

                  {/* Quick AI Learning Actions */}
                  <div style={{ display: 'flex', gap: '0.4rem', flexShrink: 0 }}>
                    <button
                      className="btn btn-sm btn-secondary"
                      style={{ fontSize: '0.78rem', padding: '0.3rem 0.6rem' }}
                      title="Explain this question simply"
                      onClick={() => onSelectQuestionForAI(q.canonical_text, 'explain')}
                    >
                      <Lightbulb size={13} style={{ color: '#f59e0b' }} />
                      <span>Explain</span>
                    </button>

                    <button
                      className="btn btn-sm btn-secondary"
                      style={{ fontSize: '0.78rem', padding: '0.3rem 0.6rem' }}
                      title="Write and evaluate my answer"
                      onClick={() => onSelectQuestionForAI(q.canonical_text, 'evaluate')}
                    >
                      <Award size={13} style={{ color: '#8b5cf6' }} />
                      <span>Evaluate</span>
                    </button>

                    <button
                      className="btn btn-sm btn-primary"
                      style={{ fontSize: '0.78rem', padding: '0.3rem 0.6rem' }}
                      title="Ask AI study tutor"
                      onClick={() => onSelectQuestionForAI(q.canonical_text, 'ask')}
                    >
                      <BrainCircuit size={13} />
                      <span>Ask AI</span>
                    </button>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.75rem', flexWrap: 'wrap' }}>
                  {q.marks && <span className="badge badge-info">{q.marks}</span>}
                  {q.section && <span className="badge badge-warning">{q.section}</span>}
                  {q.topic && <span className="badge badge-primary">{q.topic}</span>}

                  <button
                    onClick={() => toggleOccurrences(q.id)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#818cf8',
                      cursor: 'pointer',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      marginLeft: 'auto',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.3rem',
                    }}
                  >
                    <span>
                      Appears in {q.occurrences_count} paper{q.occurrences_count > 1 ? 's' : ''}
                    </span>
                    {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>
                </div>

                {/* Expandable Occurrences */}
                {isExpanded && (
                  <div
                    style={{
                      marginTop: '0.85rem',
                      padding: '0.75rem 1rem',
                      background: 'var(--bg-input)',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--border)',
                      fontSize: '0.85rem',
                    }}
                  >
                    <div style={{ fontWeight: 600, marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>
                      Exam Paper Occurrences:
                    </div>
                    {q.occurrences.map((occ, oIdx) => (
                      <div
                        key={oIdx}
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          padding: '0.3rem 0',
                          borderBottom: oIdx < q.occurrences.length - 1 ? '1px solid rgba(255, 255, 255, 0.04)' : 'none',
                        }}
                      >
                        <span>
                          <strong style={{ color: 'var(--text-primary)' }}>{occ.paper_name}</strong>
                          {occ.original_number ? ` — Q.${occ.original_number}` : ''}
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
