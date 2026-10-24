import React from 'react';

export default function Navbar({ activeTab, setActiveTab, pendingReviewCount = 0 }) {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'upload', label: 'Upload Papers & Docs', icon: '📁' },
    { id: 'duplicates', label: 'Duplicate Review', icon: '🔍', badge: pendingReviewCount },
    { id: 'bank', label: 'Question Bank', icon: '📚' },
    { id: 'assistant', label: 'AI Study Assistant', icon: '✨' },
  ];

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <span className="brand-icon">🎓</span>
        <span className="brand-title">Source2Study</span>
        <span className="brand-badge">v2.0 Unified</span>
      </div>

      <div className="nav-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
            {tab.badge > 0 && <span className="tab-badge">{tab.badge}</span>}
          </button>
        ))}
      </div>
    </nav>
  );
}
