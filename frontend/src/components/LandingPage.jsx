import React from 'react';
import {
  BrainCircuit,
  FileText,
  Youtube,
  Globe,
  HelpCircle,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  BookOpen,
  LayoutDashboard,
  ShieldCheck,
  Zap,
} from 'lucide-react';

export default function LandingPage({ setActiveTab }) {
  return (
    <div>
      {/* Hero Section */}
      <section className="landing-hero">
        <div className="landing-pill">
          <Sparkles size={15} style={{ color: '#818cf8' }} />
          <span>Next-Gen RAG Study Assistant</span>
        </div>

        <h1 className="landing-title">
          Turn Any Learning Resource into an{' '}
          <span className="text-gradient">Interactive AI Tutor</span>
        </h1>

        <p className="landing-desc">
          Upload PDFs, Word documents, YouTube lectures, or web articles. Source2Study extracts and indexes your materials into a private knowledge base, giving you 100% grounded explanations, conversational Q&A, custom quizzes, and answer evaluations with citations.
        </p>

        <div className="landing-actions">
          <button
            className="btn btn-primary btn-lg"
            onClick={() => setActiveTab('assistant')}
          >
            <span>Launch AI Workspace</span>
            <ArrowRight size={18} />
          </button>

          <button
            className="btn btn-secondary btn-lg"
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={18} />
            <span>Open Dashboard</span>
          </button>
        </div>

        {/* Supported Learning Formats */}
        <div className="landing-formats-bar">
          <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Supported Ingest:
          </span>
          <div className="format-item">
            <FileText size={16} style={{ color: '#ef4444' }} />
            <span>PDF Documents</span>
          </div>
          <div className="format-item">
            <FileText size={16} style={{ color: '#3b82f6' }} />
            <span>Word DOCX</span>
          </div>
          <div className="format-item">
            <Youtube size={16} style={{ color: '#f43f5e' }} />
            <span>YouTube Lectures</span>
          </div>
          <div className="format-item">
            <Globe size={16} style={{ color: '#10b981' }} />
            <span>Web Articles & URLs</span>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="steps-section">
        <div className="section-header" style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            How Source2Study Works
          </h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto' }}>
            A complete retrieval-augmented learning workflow built for deep retention and zero hallucinations.
          </p>
        </div>

        <div className="steps-grid">
          <div className="step-card">
            <div className="step-number">01</div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Upload Your Material
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>
              Drop textbook chapters, slide decks, previous year papers, or paste video links. We automatically parse structure, text, and tables.
            </p>
          </div>

          <div className="step-card">
            <div className="step-number">02</div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Vector RAG Indexing
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>
              Content is cleaned, chunked with semantic overlap, and embedded into local FAISS vector stores with document-level source tracking.
            </p>
          </div>

          <div className="step-card">
            <div className="step-number">03</div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Learn & Test Yourself
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>
              Chat with your tutor, ask for simpler analogies, take tailored quizzes, or submit written answers to receive instant rubric-based AI grading.
            </p>
          </div>
        </div>
      </section>

      {/* Core Feature Highlights */}
      <section style={{ margin: '3rem 0' }}>
        <div className="section-header" style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            Designed for Meaningful Learning
          </h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '650px', margin: '0 auto' }}>
            Everything you need to master tough subjects, retain key formulas, and prepare effectively for exams.
          </p>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon-box">
              <BrainCircuit size={24} />
            </div>
            <h3 className="feature-title">Grounded AI Chat</h3>
            <p className="feature-desc">
              Ask deep questions or follow-ups. Every answer is grounded directly in your uploaded notes with exact source citations and page references.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon-box">
              <Zap size={24} />
            </div>
            <h3 className="feature-title">Concept Explainer</h3>
            <p className="feature-desc">
              Stuck on an intimidating concept? Request beginner-friendly analogies, step-by-step mathematical breakdowns, or high-yield exam summaries.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon-box">
              <FileText size={24} />
            </div>
            <h3 className="feature-title">One-Click Summarizer</h3>
            <p className="feature-desc">
              Generate structured summaries with bullet points, definitions, and formulas directly from any selected document or lecture.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon-box">
              <HelpCircle size={24} />
            </div>
            <h3 className="feature-title">Dynamic Practice Quizzes</h3>
            <p className="feature-desc">
              Generate custom MCQs with adjustable difficulty. Receive immediate explanations for each answer, score tracking, and performance analysis.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon-box">
              <CheckCircle2 size={24} />
            </div>
            <h3 className="feature-title">AI Answer Evaluator</h3>
            <p className="feature-desc">
              Practice descriptive questions by typing your own answers. Get graded on a 10-point rubric with strengths, missing points, and ideal model answers.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon-box">
              <BookOpen size={24} />
            </div>
            <h3 className="feature-title">Unified Question Bank</h3>
            <p className="feature-desc">
              Upload multiple past exams. Automatic duplicate detection merges repeated questions, builds a consolidated question bank, and exports to PDF or Excel.
            </p>
          </div>
        </div>
      </section>

      {/* Call to Action Banner */}
      <section
        className="card"
        style={{
          background: 'linear-gradient(135deg, rgba(79, 70, 229, 0.2) 0%, rgba(147, 51, 234, 0.15) 100%)',
          border: '1px solid var(--primary-border)',
          padding: '3rem 2rem',
          textAlign: 'center',
          margin: '3rem 0',
        }}
      >
        <h2 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.75rem' }}>
          Ready to supercharge your study sessions?
        </h2>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto 2rem' }}>
          Start by uploading your first syllabus, lecture slides, or exam paper. Your personal AI tutor is ready.
        </p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button
            className="btn btn-primary btn-lg"
            onClick={() => setActiveTab('upload')}
          >
            <FolderUp size={18} />
            <span>Upload Materials</span>
          </button>
          <button
            className="btn btn-secondary btn-lg"
            onClick={() => setActiveTab('assistant')}
          >
            <BrainCircuit size={18} />
            <span>Open AI Assistant</span>
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <div>
            <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <GraduationCap size={18} style={{ color: '#818cf8' }} />
              <span>Source2Study — AI-Powered Learning Assistant</span>
            </div>
            <div>Built for students and educators with LangChain, FAISS, and FastAPI.</div>
          </div>
          <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
            <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('dashboard')}>Dashboard</span>
            <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('upload')}>Upload</span>
            <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('assistant')}>AI Tutor</span>
            <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('bank')}>Question Bank</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
