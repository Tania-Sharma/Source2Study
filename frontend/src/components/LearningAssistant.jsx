import React, { useState, useEffect, useRef } from 'react';
import { api } from '../api';

export default function LearningAssistant({ initialQuestion, initialAction, showToast }) {
  const [conversations, setConversations] = useState([]);
  const [currentConvId, setCurrentConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputQuery, setInputQuery] = useState('');
  const [isSending, setIsSending] = useState(false);

  // Tab mode within Assistant: 'chat' | 'explain' | 'quiz'
  const [assistantMode, setAssistantMode] = useState('chat');

  // Explain State
  const [explainTopic, setExplainTopic] = useState('');
  const [explainResult, setExplainResult] = useState(null);
  const [isExplaining, setIsExplaining] = useState(false);

  // Quiz State
  const [quizTopic, setQuizTopic] = useState('');
  const [quizData, setQuizData] = useState(null);
  const [userAnswers, setUserAnswers] = useState({});
  const [quizEvaluation, setQuizEvaluation] = useState(null);
  const [isGeneratingQuiz, setIsGeneratingQuiz] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load conversations on mount
  useEffect(() => {
    initConversations();
  }, []);

  // Handle incoming selection from QuestionBank
  useEffect(() => {
    if (initialQuestion) {
      if (initialAction === 'explain') {
        setAssistantMode('explain');
        setExplainTopic(initialQuestion);
        handleExplain(initialQuestion);
      } else {
        setAssistantMode('chat');
        setInputQuery(initialQuestion);
      }
    }
  }, [initialQuestion, initialAction]);

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

  const createNewChat = async () => {
    try {
      const conv = await api.createConversation('student_user', `Chat ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`);
      setCurrentConvId(conv.conversation_id);
      setMessages([
        {
          role: 'assistant',
          content: 'Hello! I am your Source2Study learning assistant. Ask me questions about your uploaded textbooks, lecture notes, or question papers!',
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
    } catch {
      // fallback
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
          content: `⚠️ Error generating response: ${err.message}. Please verify your GEMINI_API_KEY if testing against live LLM, or upload documents to query against.`,
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleExplain = async (topicToUse) => {
    const topic = topicToUse || explainTopic;
    if (!topic.trim()) return;
    setIsExplaining(true);
    setExplainResult(null);

    try {
      const res = await api.explain(topic);
      setExplainResult(res);
    } catch (err) {
      showToast(`Failed to get explanation: ${err.message}`, 'error');
    } finally {
      setIsExplaining(false);
    }
  };

  const handleGenerateMCQ = async () => {
    setIsGeneratingQuiz(true);
    setQuizData(null);
    setQuizEvaluation(null);
    setUserAnswers({});

    try {
      const res = await api.generateMCQ(quizTopic || 'General Quiz', 3, 'medium');
      setQuizData(res);
    } catch (err) {
      showToast(`Failed to generate quiz: ${err.message}`, 'error');
    } finally {
      setIsGeneratingQuiz(false);
    }
  };

  const handleEvaluateQuiz = async () => {
    if (!quizData || !quizData.questions) return;
    const answersList = quizData.questions.map((_, idx) => userAnswers[idx] || null);
    try {
      const evalRes = await api.evaluateQuiz(quizData.questions, answersList);
      setQuizEvaluation(evalRes);
    } catch (err) {
      showToast(`Evaluation error: ${err.message}`, 'error');
    }
  };

  return (
    <div>
      <div className="section-header">
        <h1 className="section-title">
          <span>✨</span> AI-Powered Learning Assistant
        </h1>
        <p className="section-subtitle">
          Ask questions, get simpler explanations, or generate quizzes. Every answer is grounded only in your own study materials with source citations.
        </p>
      </div>

      {/* Mode Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
        <button
          className={`btn ${assistantMode === 'chat' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
          onClick={() => setAssistantMode('chat')}
        >
          💬 Conversational Q&A
        </button>
        <button
          className={`btn ${assistantMode === 'explain' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
          onClick={() => setAssistantMode('explain')}
        >
          💡 Explain Simply
        </button>
        <button
          className={`btn ${assistantMode === 'quiz' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
          onClick={() => setAssistantMode('quiz')}
        >
          🎯 Generate Quiz
        </button>
      </div>

      {/* MODE 1: CHAT */}
      {assistantMode === 'chat' && (
        <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: '1.5rem' }}>
          {/* Conversation Sidebar */}
          <div className="card" style={{ padding: '1rem', display: 'flex', flexDirection: 'column', height: '550px' }}>
            <button className="btn btn-primary btn-sm" style={{ marginBottom: '1rem', width: '100%' }} onClick={createNewChat}>
              + New Conversation
            </button>
            <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {conversations.map((c) => (
                <button
                  key={c.conversation_id}
                  onClick={() => selectConversation(c.conversation_id)}
                  style={{
                    textAlign: 'left',
                    padding: '0.6rem 0.8rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid',
                    borderColor: currentConvId === c.conversation_id ? 'var(--primary)' : 'transparent',
                    background: currentConvId === c.conversation_id ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                    color: currentConvId === c.conversation_id ? 'var(--primary)' : 'var(--text-secondary)',
                    fontSize: '0.85rem',
                    cursor: 'pointer',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  💬 {c.title || 'Conversation'}
                </button>
              ))}
            </div>
          </div>

          {/* Chat Window */}
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
                    <div style={{ marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.1)', fontSize: '0.75rem' }}>
                      <span style={{ fontWeight: 600, color: 'var(--primary)' }}>📎 Sources cited: </span>
                      {m.sources.join(', ')}
                    </div>
                  )}
                </div>
              ))}
              {isSending && (
                <div className="chat-bubble chat-bubble-assistant" style={{ color: 'var(--text-muted)' }}>
                  Thinking & retrieving context from your documents...
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <form className="chat-input-bar" onSubmit={handleSendMessage}>
              <input
                type="text"
                className="chat-input"
                placeholder="Ask a question about your study documents..."
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                disabled={isSending}
              />
              <button type="submit" className="btn btn-primary" disabled={isSending || !inputQuery.trim()}>
                Send &rarr;
              </button>
            </form>
          </div>
        </div>
      )}

      {/* MODE 2: EXPLAIN SIMPLY */}
      {assistantMode === 'explain' && (
        <div className="card">
          <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Simpler Concept Explanation</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
            Enter a difficult concept, question, or term from your materials to get an intuitive explanation without jargon.
          </p>

          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <input
              type="text"
              className="search-input"
              style={{ flex: 1 }}
              placeholder="e.g. Overfitting, Gradient Descent, Bayes Theorem..."
              value={explainTopic}
              onChange={(e) => setExplainTopic(e.target.value)}
            />
            <button className="btn btn-primary" onClick={() => handleExplain()} disabled={isExplaining || !explainTopic.trim()}>
              {isExplaining ? 'Explaining...' : 'Explain in Simple Terms'}
            </button>
          </div>

          {explainResult && (
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', padding: '1.5rem' }}>
              <h4 style={{ color: 'var(--primary)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span>💡</span> Explanation for "{explainTopic}":
              </h4>
              <p style={{ lineHeight: 1.7, whiteSpace: 'pre-wrap', color: 'var(--text-primary)' }}>
                {explainResult.explanation}
              </p>
              {explainResult.sources && explainResult.sources.length > 0 && (
                <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Sources: {explainResult.sources.join(', ')}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* MODE 3: GENERATE QUIZ */}
      {assistantMode === 'quiz' && (
        <div className="card">
          <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Practice Quiz & MCQs</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
            Test your knowledge by generating practice questions grounded in your course documents.
          </p>

          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <input
              type="text"
              className="search-input"
              style={{ flex: 1 }}
              placeholder="Topic (e.g. Supervised Learning, Relational Databases...)"
              value={quizTopic}
              onChange={(e) => setQuizTopic(e.target.value)}
            />
            <button className="btn btn-primary" onClick={handleGenerateMCQ} disabled={isGeneratingQuiz}>
              {isGeneratingQuiz ? 'Generating...' : 'Generate Practice MCQs'}
            </button>
          </div>

          {quizData && quizData.questions && (
            <div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '1.5rem' }}>
                {quizData.questions.map((q, idx) => (
                  <div key={idx} style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border)' }}>
                    <div style={{ fontWeight: 600, marginBottom: '0.75rem' }}>
                      {idx + 1}. {q.question}
                    </div>

                    {q.options && q.options.length > 0 && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                        {q.options.map((opt, oIdx) => (
                          <label key={oIdx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.9rem' }}>
                            <input
                              type="radio"
                              name={`quiz_q_${idx}`}
                              checked={userAnswers[idx] === opt}
                              onChange={() => setUserAnswers((prev) => ({ ...prev, [idx]: opt }))}
                            />
                            {opt}
                          </label>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <button className="btn btn-success" onClick={handleEvaluateQuiz}>
                Submit Answers for Grading
              </button>
            </div>
          )}

          {quizEvaluation && (
            <div style={{ marginTop: '1.5rem', padding: '1.5rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid var(--success)', borderRadius: 'var(--radius-md)' }}>
              <h4 style={{ color: 'var(--success)', marginBottom: '0.5rem' }}>
                Score: {quizEvaluation.correct_answers} / {quizEvaluation.total_questions} ({quizEvaluation.percentage}%)
              </h4>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                {quizEvaluation.feedback}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
