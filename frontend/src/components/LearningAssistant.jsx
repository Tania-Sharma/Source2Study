import React, { useState, useEffect, useRef } from 'react';
import confetti from 'canvas-confetti';
import {
  MessageSquare,
  FileText,
  HelpCircle,
  BrainCircuit,
  CheckCircle2,
  Send,
  Plus,
  Trash2,
  Edit2,
  Check,
  X,
  Copy,
  RotateCcw,
  Sparkles,
  Search,
  BookOpen,
  ArrowRight,
  Lightbulb,
  Award,
  Layers,
  ChevronRight,
} from 'lucide-react';
import { api } from '../api';

export default function LearningAssistant({
  initialQuestion,
  initialAction,
  initialResourceId,
  showToast,
}) {
  // Context selection
  const [resources, setResources] = useState([]);
  const [selectedResourceId, setSelectedResourceId] = useState(initialResourceId || '');

  // Sub-navigation tabs: 'chat' | 'summarize' | 'explain' | 'quiz' | 'evaluate'
  const [activeMode, setActiveMode] = useState('chat');

  // Conversations (Chat Mode)
  const [conversations, setConversations] = useState([]);
  const [currentConvId, setCurrentConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputQuery, setInputQuery] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [searchConvQuery, setSearchConvQuery] = useState('');
  const [editingConvId, setEditingConvId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [convToDelete, setConvToDelete] = useState(null);

  // Summarize Mode
  const [summaryQuery, setSummaryQuery] = useState('Summarize the core concepts and key points.');
  const [summaryTopK, setSummaryTopK] = useState(5);
  const [summaryResult, setSummaryResult] = useState(null);
  const [isSummarizing, setIsSummarizing] = useState(false);

  // Explain Mode
  const [explainTopic, setExplainTopic] = useState('');
  const [explainStyle, setExplainStyle] = useState('beginner'); // 'beginner' | 'steps' | 'analogy' | 'exam'
  const [explainResult, setExplainResult] = useState(null);
  const [isExplaining, setIsExplaining] = useState(false);

  // Quiz Mode
  const [quizTopic, setQuizTopic] = useState('');
  const [quizDifficulty, setQuizDifficulty] = useState('medium');
  const [quizCount, setQuizCount] = useState(3);
  const [quizData, setQuizData] = useState(null);
  const [userAnswers, setUserAnswers] = useState({});
  const [quizEvaluation, setQuizEvaluation] = useState(null);
  const [isGeneratingQuiz, setIsGeneratingQuiz] = useState(false);
  const [isSubmittingQuiz, setIsSubmittingQuiz] = useState(false);

  // Answer Evaluator Mode
  const [evalQuestion, setEvalQuestion] = useState('');
  const [evalStudentAnswer, setEvalStudentAnswer] = useState('');
  const [evalResult, setEvalResult] = useState(null);
  const [isEvaluatingAnswer, setIsEvaluatingAnswer] = useState(false);

  const messagesEndRef = useRef(null);
  const chatInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (activeMode === 'chat') {
      scrollToBottom();
    }
  }, [messages, activeMode]);

  // Load resources & conversations on mount
  useEffect(() => {
    loadResources();
    initConversations();
  }, []);

  // Update selected resource if prop changes
  useEffect(() => {
    if (initialResourceId) {
      setSelectedResourceId(initialResourceId);
    }
  }, [initialResourceId]);

  // Handle incoming selection from Question Bank or other pages
  useEffect(() => {
    if (initialQuestion) {
      if (initialAction === 'explain') {
        setActiveMode('explain');
        setExplainTopic(initialQuestion);
        handleExplain(initialQuestion);
      } else if (initialAction === 'evaluate') {
        setActiveMode('evaluate');
        setEvalQuestion(initialQuestion);
      } else {
        setActiveMode('chat');
        setInputQuery(initialQuestion);
        chatInputRef.current?.focus();
      }
    }
  }, [initialQuestion, initialAction]);

  const loadResources = async () => {
    try {
      const data = await api.listResources();
      setResources(data || []);
    } catch (err) {
      console.warn('Failed to load resources:', err);
    }
  };

  const initConversations = async () => {
    try {
      const list = await api.listConversations();
      setConversations(list || []);
      if (list && list.length > 0) {
        selectConversation(list[0].conversation_id);
      } else {
        createNewChat();
      }
    } catch {
      createNewChat();
    }
  };

  const createNewChat = async (resourceIdToUse = selectedResourceId) => {
    try {
      const title = `Study Session ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
      const conv = await api.createConversation('student_user', title, resourceIdToUse || null);
      setCurrentConvId(conv.conversation_id);
      setMessages([
        {
          role: 'assistant',
          content: 'Hello! I am your Source2Study learning assistant. Ask me questions about your uploaded textbooks, lecture notes, or question papers! Every answer is grounded with citations.',
        },
      ]);
      const list = await api.listConversations();
      setConversations(list || []);
    } catch (err) {
      showToast(`Failed to create conversation: ${err.message}`, 'error');
    }
  };

  const selectConversation = async (id) => {
    setCurrentConvId(id);
    try {
      const conv = await api.getConversation(id);
      if (conv.resource_id) {
        setSelectedResourceId(conv.resource_id);
      }
      if (conv.history && conv.history.length > 0) {
        setMessages(conv.history);
      } else {
        setMessages([
          {
            role: 'assistant',
            content: 'Hello! Ask any question grounded in your uploaded materials.',
          },
        ]);
      }
    } catch (err) {
      console.warn('Failed to fetch conversation history:', err);
    }
  };

  const handleStartRename = (conv) => {
    setEditingConvId(conv.conversation_id);
    setEditingTitle(conv.title || '');
  };

  const handleSaveRename = async (convId) => {
    if (!editingTitle.trim()) {
      setEditingConvId(null);
      return;
    }
    try {
      await api.renameConversation(convId, editingTitle.trim());
      setConversations((prev) =>
        prev.map((c) => (c.conversation_id === convId ? { ...c, title: editingTitle.trim() } : c))
      );
      setEditingConvId(null);
      showToast('Conversation renamed.', 'success');
    } catch (err) {
      showToast(`Rename failed: ${err.message}`, 'error');
    }
  };

  const handleDeleteConversation = async () => {
    if (!convToDelete) return;
    try {
      await api.deleteConversation(convToDelete.conversation_id);
      setConversations((prev) => prev.filter((c) => c.conversation_id !== convToDelete.conversation_id));
      if (currentConvId === convToDelete.conversation_id) {
        const remaining = conversations.filter((c) => c.conversation_id !== convToDelete.conversation_id);
        if (remaining.length > 0) {
          selectConversation(remaining[0].conversation_id);
        } else {
          createNewChat();
        }
      }
      setConvToDelete(null);
      showToast('Conversation deleted.', 'success');
    } catch (err) {
      showToast(`Delete failed: ${err.message}`, 'error');
    }
  };

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!inputQuery.trim() || isSending || !currentConvId) return;

    const userText = inputQuery.trim();
    setInputQuery('');
    setMessages((prev) => [...prev, { role: 'user', content: userText }]);
    setIsSending(true);

    try {
      const res = await api.sendMessage(currentConvId, userText);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.answer,
          sources: res.sources,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ Error generating response: ${err.message}. Please verify your materials are indexed, or retry.`,
          isError: true,
          retryText: userText,
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleCopyText = (text) => {
    navigator.clipboard.writeText(text);
    showToast('Copied to clipboard!', 'success');
  };

  // Summarize handler
  const handleGenerateSummary = async () => {
    setIsSummarizing(true);
    setSummaryResult(null);
    try {
      const res = await api.summarize(
        summaryQuery,
        summaryTopK,
        selectedResourceId || null
      );
      setSummaryResult(res);
      showToast('Summary generated!', 'success');
    } catch (err) {
      showToast(`Summary error: ${err.message}`, 'error');
    } finally {
      setIsSummarizing(false);
    }
  };

  // Explain handler
  const handleExplain = async (overrideTopic) => {
    const topicToUse = overrideTopic || explainTopic;
    if (!topicToUse.trim()) return;
    setIsExplaining(true);
    setExplainResult(null);
    try {
      const res = await api.explain(
        topicToUse,
        explainStyle,
        5,
        selectedResourceId || null
      );
      setExplainResult(res);
      showToast('Explanation ready!', 'success');
    } catch (err) {
      showToast(`Explanation error: ${err.message}`, 'error');
    } finally {
      setIsExplaining(false);
    }
  };

  // Quiz handlers
  const handleGenerateMCQ = async () => {
    setIsGeneratingQuiz(true);
    setQuizData(null);
    setQuizEvaluation(null);
    setUserAnswers({});
    try {
      const res = await api.generateMCQ(
        quizTopic.trim() || null,
        quizCount,
        quizDifficulty,
        5,
        selectedResourceId || null
      );
      setQuizData(res);
      showToast(`Generated ${res.questions?.length || 0} practice questions!`, 'success');
    } catch (err) {
      showToast(`Quiz generation failed: ${err.message}`, 'error');
    } finally {
      setIsGeneratingQuiz(false);
    }
  };

  const handleEvaluateQuiz = async () => {
    if (!quizData?.questions || quizData.questions.length === 0) return;
    const answersList = quizData.questions.map((_, idx) => userAnswers[idx] || null);
    setIsSubmittingQuiz(true);
    try {
      const evalRes = await api.evaluateQuiz(quizData.questions, answersList);
      setQuizEvaluation(evalRes);
      if (evalRes.percentage >= 70) {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
        });
      }
      showToast('Quiz submitted and graded!', 'success');
    } catch (err) {
      showToast(`Evaluation error: ${err.message}`, 'error');
    } finally {
      setIsSubmittingQuiz(false);
    }
  };

  // Answer Evaluation handler
  const handleEvaluateAnswer = async (e) => {
    e?.preventDefault();
    if (!evalQuestion.trim() || !evalStudentAnswer.trim()) {
      showToast('Please enter both the question and your answer.', 'error');
      return;
    }
    setIsEvaluatingAnswer(true);
    setEvalResult(null);
    try {
      const res = await api.evaluateAnswer(
        evalQuestion,
        evalStudentAnswer,
        selectedResourceId || null
      );
      setEvalResult(res);
      if (res.score >= 7) {
        confetti({
          particleCount: 50,
          spread: 60,
          origin: { y: 0.6 },
        });
      }
      showToast('Answer evaluated by AI tutor!', 'success');
    } catch (err) {
      showToast(`Evaluation error: ${err.message}`, 'error');
    } finally {
      setIsEvaluatingAnswer(false);
    }
  };

  const filteredConversations = conversations.filter((c) =>
    (c.title || '').toLowerCase().includes(searchConvQuery.toLowerCase())
  );

  return (
    <div className="workspace-container">
      {/* Top Context & Resource Selector Bar */}
      <div className="workspace-context-bar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#818cf8', fontWeight: 600, fontSize: '0.9rem' }}>
            <Layers size={18} />
            <span>Learning Context:</span>
          </div>

          <select
            className="select-input"
            style={{ minWidth: '260px', width: 'auto', padding: '0.45rem 0.85rem', fontSize: '0.85rem' }}
            value={selectedResourceId}
            onChange={(e) => setSelectedResourceId(e.target.value)}
          >
            <option value="">🌐 Entire Knowledge Base (All Materials)</option>
            {resources.map((r) => (
              <option key={r.id} value={r.id}>
                📄 {r.source_name || r.url} ({r.source_type?.toUpperCase()})
              </option>
            ))}
          </select>

          {selectedResourceId && (
            <button
              className="btn btn-sm btn-outline"
              style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
              onClick={() => setSelectedResourceId('')}
            >
              Clear Focus
            </button>
          )}
        </div>

        {/* Workspace Mode Navigation Tabs */}
        <div className="workspace-mode-nav">
          <button
            className={`btn btn-sm ${activeMode === 'chat' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveMode('chat')}
          >
            <MessageSquare size={14} />
            <span>AI Tutor Chat</span>
          </button>

          <button
            className={`btn btn-sm ${activeMode === 'summarize' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveMode('summarize')}
          >
            <FileText size={14} />
            <span>Summarizer</span>
          </button>

          <button
            className={`btn btn-sm ${activeMode === 'explain' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveMode('explain')}
          >
            <Lightbulb size={14} />
            <span>Concept Explainer</span>
          </button>

          <button
            className={`btn btn-sm ${activeMode === 'quiz' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveMode('quiz')}
          >
            <HelpCircle size={14} />
            <span>Practice Quiz</span>
          </button>

          <button
            className={`btn btn-sm ${activeMode === 'evaluate' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveMode('evaluate')}
          >
            <Award size={14} />
            <span>Answer Evaluator</span>
          </button>
        </div>
      </div>

      {/* Main Workspace Body */}
      {/* MODE 1: CHAT */}
      {activeMode === 'chat' && (
        <div className="workspace-body">
          {/* Conversation Sidebar */}
          <div className="chat-sidebar">
            <button
              className="btn btn-primary"
              style={{ width: '100%', marginBottom: '0.75rem' }}
              onClick={() => createNewChat()}
            >
              <Plus size={16} />
              <span>New Conversation</span>
            </button>

            {/* Conversation Search Filter */}
            <div style={{ position: 'relative', marginBottom: '0.5rem' }}>
              <input
                type="text"
                className="input-text"
                style={{ paddingLeft: '2rem', fontSize: '0.8rem', padding: '0.45rem 0.75rem 0.45rem 2rem' }}
                placeholder="Search sessions..."
                value={searchConvQuery}
                onChange={(e) => setSearchConvQuery(e.target.value)}
              />
              <Search
                size={14}
                style={{ position: 'absolute', left: '0.65rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}
              />
            </div>

            {/* Conversation List */}
            <div className="chat-list">
              {filteredConversations.length > 0 ? (
                filteredConversations.map((conv) => (
                  <div
                    key={conv.conversation_id}
                    className={`chat-item ${currentConvId === conv.conversation_id ? 'active' : ''}`}
                    onClick={() => selectConversation(conv.conversation_id)}
                  >
                    {editingConvId === conv.conversation_id ? (
                      <div
                        style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', width: '100%' }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        <input
                          type="text"
                          className="input-text"
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.8rem' }}
                          value={editingTitle}
                          onChange={(e) => setEditingTitle(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleSaveRename(conv.conversation_id);
                            if (e.key === 'Escape') setEditingConvId(null);
                          }}
                          autoFocus
                        />
                        <button
                          className="btn btn-sm btn-primary btn-icon"
                          onClick={() => handleSaveRename(conv.conversation_id)}
                          title="Save"
                        >
                          <Check size={12} />
                        </button>
                        <button
                          className="btn btn-sm btn-secondary btn-icon"
                          onClick={() => setEditingConvId(null)}
                          title="Cancel"
                        >
                          <X size={12} />
                        </button>
                      </div>
                    ) : (
                      <>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', overflow: 'hidden' }}>
                          <MessageSquare size={14} style={{ flexShrink: 0 }} />
                          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {conv.title || 'Untitled Session'}
                          </span>
                        </div>

                        <div className="chat-item-actions" onClick={(e) => e.stopPropagation()}>
                          <button
                            className="btn btn-icon btn-secondary"
                            style={{ padding: '0.25rem' }}
                            onClick={() => handleStartRename(conv)}
                            title="Rename Conversation"
                          >
                            <Edit2 size={12} />
                          </button>
                          <button
                            className="btn btn-icon btn-danger"
                            style={{ padding: '0.25rem' }}
                            onClick={() => setConvToDelete(conv)}
                            title="Delete Conversation"
                          >
                            <Trash2 size={12} />
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                ))
              ) : (
                <div style={{ textAlign: 'center', padding: '1.5rem 0.5rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  No conversations found
                </div>
              )}
            </div>
          </div>

          {/* Main Chat Area */}
          <div className="chat-window">
            <div className="chat-messages">
              {messages.map((m, idx) => (
                <div
                  key={idx}
                  className={`chat-bubble ${m.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'}`}
                >
                  <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>

                  {/* Sources citation pill */}
                  {m.sources && m.sources.length > 0 && (
                    <div className="chat-sources-box">
                      <span style={{ fontWeight: 600, color: '#818cf8', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <BookOpen size={12} /> Citations:
                      </span>
                      {m.sources.map((src, sIdx) => (
                        <span
                          key={sIdx}
                          style={{
                            background: 'rgba(99, 102, 241, 0.15)',
                            padding: '0.15rem 0.5rem',
                            borderRadius: 'var(--radius-full)',
                            fontSize: '0.72rem',
                            color: '#c7d2fe',
                          }}
                        >
                          {src}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Action buttons (Copy / Retry) */}
                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                    <button
                      className="btn btn-sm btn-icon"
                      style={{ background: 'transparent', color: 'var(--text-muted)', padding: '0.15rem 0.4rem' }}
                      onClick={() => handleCopyText(m.content)}
                      title="Copy response"
                    >
                      <Copy size={12} />
                    </button>
                    {m.isError && m.retryText && (
                      <button
                        className="btn btn-sm btn-secondary"
                        style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                        onClick={() => {
                          setInputQuery(m.retryText);
                          chatInputRef.current?.focus();
                        }}
                      >
                        <RotateCcw size={11} /> Retry
                      </button>
                    )}
                  </div>
                </div>
              ))}

              {isSending && (
                <div className="chat-bubble chat-bubble-assistant" style={{ color: 'var(--text-muted)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Sparkles size={16} className="spin-animation" style={{ color: '#818cf8' }} />
                    <span>Retrieving context from materials & generating grounded answer...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Suggestion Chips */}
            <div className="suggestion-chips">
              <button
                className="chip-btn"
                onClick={() => setInputQuery('Explain this in simpler terms with a real-world analogy.')}
              >
                💡 Explain simpler
              </button>
              <button
                className="chip-btn"
                onClick={() => setInputQuery('Summarize the 3 most important takeaways from this topic.')}
              >
                📝 Key takeaways
              </button>
              <button
                className="chip-btn"
                onClick={() => setInputQuery('Give me a concrete step-by-step example.')}
              >
                🔍 Give an example
              </button>
              <button
                className="chip-btn"
                onClick={() => setInputQuery('What questions are likely to be asked about this in an exam?')}
              >
                🎯 Likely exam questions
              </button>
            </div>

            {/* Chat Input Bar */}
            <form className="chat-input-bar" onSubmit={handleSendMessage}>
              <input
                ref={chatInputRef}
                type="text"
                className="chat-input"
                placeholder="Ask any question grounded in your course documents... (Enter to send, Shift+Enter for newline)"
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isSending}
              />
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isSending || !inputQuery.trim()}
              >
                <Send size={16} />
                <span>Send</span>
              </button>
            </form>
          </div>
        </div>
      )}

      {/* MODE 2: SUMMARIZER */}
      {activeMode === 'summarize' && (
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <FileText size={22} style={{ color: '#818cf8' }} />
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Grounded Document Summarizer</h3>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: 1.6 }}>
            Generate structured, revision-ready summaries with key concepts, definitions, and formulas directly from your selected materials.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '1rem', marginBottom: '1.5rem' }}>
            <div>
              <label className="input-label" style={{ marginBottom: '0.4rem', display: 'block' }}>
                Summary Query / Focus Area:
              </label>
              <input
                type="text"
                className="input-text"
                value={summaryQuery}
                onChange={(e) => setSummaryQuery(e.target.value)}
                placeholder="e.g. Summarize main concepts, formulas, and architecture..."
              />
            </div>

            <div>
              <label className="input-label" style={{ marginBottom: '0.4rem', display: 'block' }}>
                Context Depth (Chunks):
              </label>
              <select
                className="select-input"
                value={summaryTopK}
                onChange={(e) => setSummaryTopK(Number(e.target.value))}
              >
                <option value={3}>3 chunks (Concise)</option>
                <option value={5}>5 chunks (Standard)</option>
                <option value={8}>8 chunks (Comprehensive)</option>
              </select>
            </div>
          </div>

          <button
            className="btn btn-primary"
            disabled={isSummarizing || !summaryQuery.trim()}
            onClick={handleGenerateSummary}
          >
            {isSummarizing ? (
              <>
                <Sparkles size={16} className="spin-animation" />
                <span>Synthesizing Summary...</span>
              </>
            ) : (
              <>
                <FileText size={16} />
                <span>Generate Grounded Summary</span>
              </>
            )}
          </button>

          {summaryResult && (
            <div style={{ marginTop: '2rem', background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', padding: '1.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h4 style={{ color: '#818cf8', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Sparkles size={16} /> Generated Summary
                </h4>
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={() => handleCopyText(summaryResult.summary)}
                >
                  <Copy size={13} />
                  <span>Copy</span>
                </button>
              </div>

              <div style={{ lineHeight: 1.7, whiteSpace: 'pre-wrap', color: 'var(--text-primary)', fontSize: '0.95rem' }}>
                {summaryResult.summary}
              </div>

              {summaryResult.sources && summaryResult.sources.length > 0 && (
                <div style={{ marginTop: '1.25rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255, 255, 255, 0.08)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  <strong style={{ color: 'var(--text-secondary)' }}>Sources Cited: </strong>
                  {summaryResult.sources.join(', ')}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* MODE 3: CONCEPT EXPLAINER */}
      {activeMode === 'explain' && (
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <Lightbulb size={22} style={{ color: '#f59e0b' }} />
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Intuitive Concept Explainer</h3>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: 1.6 }}>
            Break down complex or confusing concepts using tailored explanation styles grounded in your course materials.
          </p>

          <div style={{ marginBottom: '1.25rem' }}>
            <label className="input-label" style={{ marginBottom: '0.4rem', display: 'block' }}>
              Concept or Term to Explain:
            </label>
            <input
              type="text"
              className="input-text"
              value={explainTopic}
              onChange={(e) => setExplainTopic(e.target.value)}
              placeholder="e.g. Overfitting, PageRank Algorithm, Gradient Descent, Normalization..."
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label className="input-label" style={{ marginBottom: '0.4rem', display: 'block' }}>
              Explanation Style:
            </label>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              {[
                { id: 'beginner', label: '🌱 Beginner-Friendly (Zero Jargon)' },
                { id: 'steps', label: '🪜 Step-by-Step Breakdown' },
                { id: 'analogy', label: '💡 Real-World Analogy' },
                { id: 'exam', label: '🎯 High-Yield Exam Prep' },
              ].map((style) => (
                <button
                  key={style.id}
                  className={`btn btn-sm ${explainStyle === style.id ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setExplainStyle(style.id)}
                >
                  {style.label}
                </button>
              ))}
            </div>
          </div>

          <button
            className="btn btn-primary"
            disabled={isExplaining || !explainTopic.trim()}
            onClick={() => handleExplain()}
          >
            {isExplaining ? (
              <>
                <Sparkles size={16} className="spin-animation" />
                <span>Explaining Concept...</span>
              </>
            ) : (
              <>
                <Lightbulb size={16} />
                <span>Explain Concept</span>
              </>
            )}
          </button>

          {explainResult && (
            <div style={{ marginTop: '2rem', background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', padding: '1.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h4 style={{ color: '#f59e0b', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Lightbulb size={16} /> Explanation: "{explainTopic}"
                </h4>
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={() => handleCopyText(explainResult.explanation)}
                >
                  <Copy size={13} />
                  <span>Copy</span>
                </button>
              </div>

              <div style={{ lineHeight: 1.7, whiteSpace: 'pre-wrap', color: 'var(--text-primary)', fontSize: '0.95rem' }}>
                {explainResult.explanation}
              </div>

              {explainResult.sources && explainResult.sources.length > 0 && (
                <div style={{ marginTop: '1.25rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255, 255, 255, 0.08)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  <strong style={{ color: 'var(--text-secondary)' }}>Sources: </strong>
                  {explainResult.sources.join(', ')}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* MODE 4: PRACTICE QUIZ & MCQS */}
      {activeMode === 'quiz' && (
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <HelpCircle size={22} style={{ color: '#10b981' }} />
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Practice Quiz & MCQ Generator</h3>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: 1.6 }}>
            Generate multiple-choice practice quizzes from your study documents. Answer questions and receive instant evaluation.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto auto', gap: '1rem', marginBottom: '1.5rem' }}>
            <div>
              <label className="input-label" style={{ marginBottom: '0.4rem', display: 'block' }}>
                Topic Focus (Optional):
              </label>
              <input
                type="text"
                className="input-text"
                value={quizTopic}
                onChange={(e) => setQuizTopic(e.target.value)}
                placeholder="Leave blank to cover all topics in the document..."
              />
            </div>

            <div>
              <label className="input-label" style={{ marginBottom: '0.4rem', display: 'block' }}>
                Difficulty:
              </label>
              <select
                className="select-input"
                value={quizDifficulty}
                onChange={(e) => setQuizDifficulty(e.target.value)}
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>

            <div>
              <label className="input-label" style={{ marginBottom: '0.4rem', display: 'block' }}>
                Question Count:
              </label>
              <select
                className="select-input"
                value={quizCount}
                onChange={(e) => setQuizCount(Number(e.target.value))}
              >
                <option value={3}>3 Questions</option>
                <option value={5}>5 Questions</option>
                <option value={10}>10 Questions</option>
              </select>
            </div>
          </div>

          <button
            className="btn btn-primary"
            disabled={isGeneratingQuiz}
            onClick={handleGenerateMCQ}
          >
            {isGeneratingQuiz ? (
              <>
                <Sparkles size={16} className="spin-animation" />
                <span>Generating Quiz...</span>
              </>
            ) : (
              <>
                <HelpCircle size={16} />
                <span>Generate Practice MCQs</span>
              </>
            )}
          </button>

          {/* Render Quiz Questions */}
          {quizData?.questions && quizData.questions.length > 0 && (
            <div style={{ marginTop: '2.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <h4 style={{ fontSize: '1.15rem', fontWeight: 600 }}>
                  {quizData.title || 'Practice Quiz'} ({quizData.questions.length} Questions)
                </h4>
                <span className="badge badge-primary">Difficulty: {quizData.difficulty || quizDifficulty}</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '2rem' }}>
                {quizData.questions.map((q, idx) => (
                  <div key={idx} className="quiz-question-card">
                    <div style={{ fontWeight: 600, fontSize: '1rem', marginBottom: '0.85rem' }}>
                      {idx + 1}. {q.question}
                    </div>

                    {q.options && q.options.length > 0 && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {q.options.map((opt, oIdx) => {
                          const isSelected = userAnswers[idx] === opt;
                          return (
                            <div
                              key={oIdx}
                              className={`mcq-option ${isSelected ? 'selected' : ''}`}
                              onClick={() => {
                                if (!quizEvaluation) {
                                  setUserAnswers((prev) => ({ ...prev, [idx]: opt }));
                                }
                              }}
                            >
                              <input
                                type="radio"
                                name={`quiz_${idx}`}
                                checked={isSelected}
                                onChange={() => {}}
                                disabled={Boolean(quizEvaluation)}
                                style={{ accentColor: '#4f46e5' }}
                              />
                              <span style={{ fontSize: '0.92rem' }}>{opt}</span>
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {/* If evaluated, show review feedback */}
                    {quizEvaluation?.results && quizEvaluation.results[idx] && (
                      <div
                        style={{
                          marginTop: '1rem',
                          padding: '0.85rem 1rem',
                          borderRadius: 'var(--radius-sm)',
                          background: quizEvaluation.results[idx].is_correct
                            ? 'rgba(16, 185, 129, 0.1)'
                            : 'rgba(239, 68, 68, 0.1)',
                          border: `1px solid ${
                            quizEvaluation.results[idx].is_correct ? 'var(--success)' : 'var(--danger)'
                          }`,
                          fontSize: '0.88rem',
                        }}
                      >
                        <div style={{ fontWeight: 600, marginBottom: '0.25rem', color: quizEvaluation.results[idx].is_correct ? 'var(--success)' : 'var(--danger)' }}>
                          {quizEvaluation.results[idx].is_correct ? '✓ Correct Answer!' : '✕ Incorrect'}
                        </div>
                        {!quizEvaluation.results[idx].is_correct && (
                          <div style={{ color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                            <strong>Correct Answer: </strong> {quizEvaluation.results[idx].correct_answer}
                          </div>
                        )}
                        {quizEvaluation.results[idx].explanation && (
                          <div style={{ color: 'var(--text-primary)', marginTop: '0.25rem' }}>
                            <strong>Explanation: </strong> {quizEvaluation.results[idx].explanation}
                          </div>
                        )}
                        {quizEvaluation.results[idx].source_reference && (
                          <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem', marginTop: '0.35rem' }}>
                            Reference: {quizEvaluation.results[idx].source_reference}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {!quizEvaluation ? (
                <button
                  className="btn btn-success btn-lg"
                  onClick={handleEvaluateQuiz}
                  disabled={isSubmittingQuiz}
                  style={{ width: '100%' }}
                >
                  {isSubmittingQuiz ? 'Grading Answers...' : 'Submit Quiz for Grading'}
                </button>
              ) : (
                <div className="scorecard-banner">
                  <h3 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--success)' }}>
                    Quiz Results: {quizEvaluation.score} / {quizEvaluation.total_questions} ({quizEvaluation.percentage}%)
                  </h3>
                  <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                    You got {quizEvaluation.correct} correct and {quizEvaluation.incorrect} incorrect.
                  </p>
                  <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                    <button
                      className="btn btn-secondary"
                      onClick={() => {
                        setUserAnswers({});
                        setQuizEvaluation(null);
                      }}
                    >
                      <RotateCcw size={16} /> Retake Quiz
                    </button>
                    <button className="btn btn-primary" onClick={handleGenerateMCQ}>
                      <Plus size={16} /> Generate New Quiz
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* MODE 5: ANSWER EVALUATOR */}
      {activeMode === 'evaluate' && (
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <Award size={22} style={{ color: '#8b5cf6' }} />
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Descriptive Answer Evaluator</h3>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: 1.6 }}>
            Type your own written answer to an exam or study question. The AI evaluates your depth, factual correctness, and assigns a 10-point rubric score with actionable improvements.
          </p>

          <form onSubmit={handleEvaluateAnswer}>
            <div style={{ marginBottom: '1.25rem' }}>
              <label className="input-label" style={{ marginBottom: '0.4rem', display: 'block' }}>
                Question:
              </label>
              <input
                type="text"
                className="input-text"
                value={evalQuestion}
                onChange={(e) => setEvalQuestion(e.target.value)}
                placeholder="e.g. Explain how gradient descent optimizes machine learning weights."
                required
              />
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label className="input-label" style={{ marginBottom: '0.4rem', display: 'block' }}>
                Your Answer:
              </label>
              <textarea
                className="textarea-input"
                style={{ minHeight: '140px' }}
                value={evalStudentAnswer}
                onChange={(e) => setEvalStudentAnswer(e.target.value)}
                placeholder="Write your answer here in complete sentences as you would on an exam..."
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={isEvaluatingAnswer || !evalQuestion.trim() || !evalStudentAnswer.trim()}
            >
              {isEvaluatingAnswer ? (
                <>
                  <Sparkles size={16} className="spin-animation" />
                  <span>Evaluating Answer with Rubric...</span>
                </>
              ) : (
                <>
                  <Award size={16} />
                  <span>Evaluate My Answer</span>
                </>
              )}
            </button>
          </form>

          {/* Evaluation Results Card */}
          {evalResult && (
            <div className="eval-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
                    <span className="badge badge-success" style={{ fontSize: '0.85rem' }}>
                      {evalResult.verdict || 'Evaluated'}
                    </span>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      Assessed against course knowledge base
                    </span>
                  </div>
                  <h4 style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    Evaluation Scorecard
                  </h4>
                </div>

                <div className="eval-score-ring">
                  {evalResult.score}/{evalResult.max_score || 10}
                </div>
              </div>

              {/* Feedback Summary */}
              <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)', marginBottom: '1.25rem', fontSize: '0.92rem', lineHeight: 1.6 }}>
                <strong>Tutor Feedback: </strong> {evalResult.feedback}
              </div>

              {/* Strengths & Improvements Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', marginBottom: '1.5rem' }}>
                <div style={{ background: 'rgba(16, 185, 129, 0.06)', border: '1px solid var(--success-border)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
                  <div style={{ fontWeight: 600, color: 'var(--success)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <CheckCircle2 size={16} /> What You Did Well:
                  </div>
                  <ul style={{ paddingLeft: '1.2rem', fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    {(evalResult.strengths || ['Good attempt']).map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div style={{ background: 'rgba(245, 158, 11, 0.06)', border: '1px solid var(--warning-border)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
                  <div style={{ fontWeight: 600, color: 'var(--warning)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Lightbulb size={16} /> Suggested Improvements:
                  </div>
                  <ul style={{ paddingLeft: '1.2rem', fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    {(evalResult.improvements || ['Add more detail']).map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Ideal Model Answer */}
              {evalResult.ideal_answer && (
                <div style={{ background: 'rgba(99, 102, 241, 0.08)', border: '1px solid var(--primary-border)', borderRadius: 'var(--radius-sm)', padding: '1.25rem' }}>
                  <div style={{ fontWeight: 600, color: '#818cf8', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <BookOpen size={16} /> Model Reference Answer:
                  </div>
                  <p style={{ fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>
                    {evalResult.ideal_answer}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Delete Conversation Confirmation Modal */}
      {convToDelete && (
        <div className="modal-overlay" onClick={() => setConvToDelete(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '0.75rem', color: 'var(--danger)' }}>
              Delete Conversation?
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: 1.6 }}>
              Are you sure you want to delete <strong style={{ color: 'var(--text-primary)' }}>{convToDelete.title}</strong>? All message history will be removed.
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button className="btn btn-secondary" onClick={() => setConvToDelete(null)}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={handleDeleteConversation}>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
