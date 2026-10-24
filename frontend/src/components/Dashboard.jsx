import React, { useState, useEffect } from 'react';
import {
  FileText,
  BrainCircuit,
  FolderUp,
  BookOpen,
  Sparkles,
  ArrowRight,
  Clock,
  CheckCircle2,
  CopyCheck,
  MessageSquare,
  HelpCircle,
  ExternalLink,
  Layers,
  Globe,
} from 'lucide-react';
import { api } from '../api';

export default function Dashboard({
  setActiveTab,
  onSelectResourceForStudy,
  onSelectConversation,
}) {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOverview();
  }, []);

  const loadOverview = async () => {
    setLoading(true);
    try {
      const data = await api.getDashboardOverview();
      setOverview(data);
    } catch (err) {
      console.warn('Dashboard stats load warning:', err);
    } finally {
      setLoading(false);
    }
  };

  const getFormatIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'youtube':
        return <Youtube size={16} style={{ color: '#f43f5e' }} />;
      case 'website':
      case 'web':
        return <Globe size={16} style={{ color: '#10b981' }} />;
      default:
        return <FileText size={16} style={{ color: '#818cf8' }} />;
    }
  };

  const qStats = overview?.question_stats || {};
  const recentResources = overview?.recent_resources || [];
  const recentConvs = overview?.recent_conversations || [];

  return (
    <div>
      {/* Header */}
      <div className="section-header">
        <div className="section-header-row">
          <div>
            <h1 className="section-title">
              <Sparkles size={28} style={{ color: '#818cf8' }} />
              <span>Learning Dashboard</span>
            </h1>
            <p className="section-subtitle">
              Monitor your study resources, ongoing learning sessions, and master question bank statistics.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              className="btn btn-secondary"
              onClick={() => setActiveTab('upload')}
            >
              <FolderUp size={16} />
              <span>Add Resource</span>
            </button>
            <button
              className="btn btn-primary"
              onClick={() => setActiveTab('assistant')}
            >
              <BrainCircuit size={16} />
              <span>Start Learning</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Real Metric Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-title">Study Resources</span>
            <span className="stat-icon"><Layers size={20} /></span>
          </div>
          <div className="stat-value">{loading ? '...' : (overview?.total_resources ?? 0)}</div>
          <span className="stat-subtext">PDF, DOCX, YouTube, Web</span>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-title">Active AI Sessions</span>
            <span className="stat-icon"><MessageSquare size={20} /></span>
          </div>
          <div className="stat-value">{loading ? '...' : (overview?.total_conversations ?? 0)}</div>
          <span className="stat-subtext">{overview?.total_messages ?? 0} total questions answered</span>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-title">Question Papers</span>
            <span className="stat-icon"><FileText size={20} /></span>
          </div>
          <div className="stat-value">{loading ? '...' : (qStats.total_papers ?? 0)}</div>
          <span className="stat-subtext">Analyzed past exams</span>
        </div>

        <div className="stat-card" style={{ borderColor: 'var(--success-border)' }}>
          <div className="stat-header">
            <span className="stat-title">Unique Question Bank</span>
            <span className="stat-icon" style={{ color: 'var(--success)' }}><CheckCircle2 size={20} /></span>
          </div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>
            {loading ? '...' : (qStats.unique_questions ?? 0)}
          </div>
          <span className="stat-subtext">Deduplicated master items</span>
        </div>

        <div className="stat-card" style={{ borderColor: 'var(--warning-border)' }}>
          <div className="stat-header">
            <span className="stat-title">Duplicates Detected</span>
            <span className="stat-icon" style={{ color: 'var(--warning)' }}><CopyCheck size={20} /></span>
          </div>
          <div className="stat-value" style={{ color: 'var(--warning)' }}>
            {loading ? '...' : ((qStats.exact_duplicates || 0) + (qStats.semantic_duplicates || 0))}
          </div>
          <span className="stat-subtext">
            {qStats.exact_duplicates || 0} exact &bull; {qStats.semantic_duplicates || 0} semantic
          </span>
        </div>
      </div>

      {/* Quick Action Cards */}
      <div className="dashboard-quick-actions">
        <div className="action-card">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <BrainCircuit size={20} style={{ color: '#818cf8' }} />
              <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>AI Tutor Chat</h3>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '1.25rem', lineHeight: 1.5 }}>
              Ask questions grounded directly in your uploaded materials. Receive clear answers with document citations.
            </p>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => setActiveTab('assistant')}
          >
            <span>Open Chat</span>
            <ArrowRight size={15} />
          </button>
        </div>

        <div className="action-card">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <HelpCircle size={20} style={{ color: '#10b981' }} />
              <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Practice Quizzes</h3>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '1.25rem', lineHeight: 1.5 }}>
              Generate practice MCQs based on your course notes. Test yourself and view full step-by-step explanations.
            </p>
          </div>
          <button
            className="btn btn-secondary"
            onClick={() => {
              setActiveTab('assistant');
            }}
          >
            <span>Take a Quiz</span>
            <ArrowRight size={15} />
          </button>
        </div>

        <div className="action-card">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <BookOpen size={20} style={{ color: '#f59e0b' }} />
              <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Question Bank</h3>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '1.25rem', lineHeight: 1.5 }}>
              Browse deduplicated questions extracted from previous years' exams. Export in CSV, Excel, or PDF format.
            </p>
          </div>
          <button
            className="btn btn-secondary"
            onClick={() => setActiveTab('bank')}
          >
            <span>Browse Bank</span>
            <ArrowRight size={15} />
          </button>
        </div>
      </div>

      {/* Two Column Grid: Recent Resources & Recent Sessions */}
      <div className="dashboard-sections-grid">
        {/* Recent Resources */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Layers size={18} style={{ color: '#818cf8' }} />
              <span>Recent Learning Materials</span>
            </h3>
            <button className="btn btn-sm btn-outline" onClick={() => setActiveTab('upload')}>
              View All
            </button>
          </div>

          {recentResources.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
              {recentResources.map((res) => (
                <div
                  key={res.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.75rem 1rem',
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-sm)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', overflow: 'hidden' }}>
                    {getFormatIcon(res.source_type)}
                    <div>
                      <div style={{ fontWeight: 500, fontSize: '0.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '240px' }}>
                        {res.source_name || res.url}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Type: {res.source_type?.toUpperCase()} &bull; {res.created_at ? new Date(res.created_at).toLocaleDateString() : 'Recent'}
                      </div>
                    </div>
                  </div>

                  <button
                    className="btn btn-sm btn-secondary"
                    onClick={() => {
                      if (onSelectResourceForStudy) {
                        onSelectResourceForStudy(res.id);
                      }
                      setActiveTab('assistant');
                    }}
                  >
                    <span>Study</span>
                    <ExternalLink size={13} />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-muted)' }}>
              <FolderUp size={36} style={{ color: 'var(--text-muted)', marginBottom: '0.75rem', opacity: 0.5 }} />
              <div style={{ fontWeight: 500, marginBottom: '0.25rem', color: 'var(--text-secondary)' }}>
                No learning materials uploaded yet
              </div>
              <p style={{ fontSize: '0.85rem', marginBottom: '1rem' }}>
                Upload your first lecture PDF, notes, or YouTube video to begin.
              </p>
              <button className="btn btn-sm btn-primary" onClick={() => setActiveTab('upload')}>
                Upload Materials
              </button>
            </div>
          )}
        </div>

        {/* Recent Chat Sessions */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Clock size={18} style={{ color: '#818cf8' }} />
              <span>Recent Study Sessions</span>
            </h3>
            <button className="btn btn-sm btn-outline" onClick={() => setActiveTab('assistant')}>
              New Chat
            </button>
          </div>

          {recentConvs.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
              {recentConvs.map((conv) => (
                <div
                  key={conv.conversation_id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.75rem 1rem',
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-sm)',
                  }}
                >
                  <div style={{ overflow: 'hidden' }}>
                    <div style={{ fontWeight: 500, fontSize: '0.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '240px' }}>
                      {conv.title || 'Study Session'}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {conv.message_count} message{conv.message_count === 1 ? '' : 's'} &bull; Updated {conv.updated_at ? new Date(conv.updated_at).toLocaleDateString() : 'Recently'}
                    </div>
                  </div>

                  <button
                    className="btn btn-sm btn-primary"
                    onClick={() => {
                      if (onSelectConversation) {
                        onSelectConversation(conv.conversation_id);
                      }
                      setActiveTab('assistant');
                    }}
                  >
                    <span>Resume</span>
                    <ArrowRight size={13} />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-muted)' }}>
              <MessageSquare size={36} style={{ color: 'var(--text-muted)', marginBottom: '0.75rem', opacity: 0.5 }} />
              <div style={{ fontWeight: 500, marginBottom: '0.25rem', color: 'var(--text-secondary)' }}>
                No active conversations yet
              </div>
              <p style={{ fontSize: '0.85rem', marginBottom: '1rem' }}>
                Start a session with your AI tutor to clarify tricky topics.
              </p>
              <button className="btn btn-sm btn-primary" onClick={() => setActiveTab('assistant')}>
                Launch AI Tutor
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
