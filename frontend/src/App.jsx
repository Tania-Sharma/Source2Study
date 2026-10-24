import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import UploadPage from './components/UploadPage';
import DuplicateReview from './components/DuplicateReview';
import QuestionBankView from './components/QuestionBankView';
import LearningAssistant from './components/LearningAssistant';
import { api } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({});
  const [papers, setPapers] = useState([]);
  const [pendingReviewCount, setPendingReviewCount] = useState(0);

  // Selected question forwarded to AI Assistant
  const [selectedQuestionForAI, setSelectedQuestionForAI] = useState(null);
  const [aiAction, setAiAction] = useState('ask');

  // Toasts
  const [toasts, setToasts] = useState([]);

  const showToast = (message, type = 'info') => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const loadData = async () => {
    try {
      const statsRes = await api.getStats();
      setStats(statsRes || {});
      setPendingReviewCount(statsRes.pending_reviews || 0);

      const papersRes = await api.getPapers();
      setPapers(papersRes || []);
    } catch (err) {
      console.warn('API sync warning:', err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSelectQuestionForAI = (text, action = 'ask') => {
    setSelectedQuestionForAI(text);
    setAiAction(action);
    setActiveTab('assistant');
  };

  return (
    <div className="app-layout">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        pendingReviewCount={pendingReviewCount}
      />

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <Dashboard
            stats={stats}
            papers={papers}
            setActiveTab={setActiveTab}
          />
        )}

        {activeTab === 'upload' && (
          <UploadPage
            onRefreshData={loadData}
            showToast={showToast}
            setActiveTab={setActiveTab}
          />
        )}

        {activeTab === 'duplicates' && (
          <DuplicateReview
            showToast={showToast}
            onRefreshData={loadData}
          />
        )}

        {activeTab === 'bank' && (
          <QuestionBankView
            papers={papers}
            onSelectQuestionForAI={handleSelectQuestionForAI}
            showToast={showToast}
          />
        )}

        {activeTab === 'assistant' && (
          <LearningAssistant
            initialQuestion={selectedQuestionForAI}
            initialAction={aiAction}
            showToast={showToast}
          />
        )}
      </main>

      {/* Floating Toast Alerts */}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className={`toast toast-${t.type}`}>
            <span>{t.type === 'success' ? '✓' : t.type === 'error' ? '✕' : 'ℹ'}</span>
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
