import React, { useState } from 'react';
import {
  GraduationCap,
  LayoutDashboard,
  FolderUp,
  BrainCircuit,
  BookOpen,
  CopyCheck,
  Home,
  Menu,
  X,
  Sparkles,
} from 'lucide-react';

export default function Navbar({
  activeTab,
  setActiveTab,
  pendingReviewCount = 0,
  isHealthy = true,
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const tabs = [
    { id: 'landing', label: 'Home', icon: Home },
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload & Resources', icon: FolderUp },
    { id: 'assistant', label: 'AI Workspace', icon: BrainCircuit, highlight: true },
    { id: 'bank', label: 'Question Bank', icon: BookOpen },
    { id: 'duplicates', label: 'Duplicate Review', icon: CopyCheck, badge: pendingReviewCount },
  ];

  const handleTabClick = (tabId) => {
    setActiveTab(tabId);
    setMobileMenuOpen(false);
  };

  return (
    <header className="navbar">
      <div className="nav-brand" onClick={() => handleTabClick('landing')}>
        <div className="brand-icon-wrapper">
          <GraduationCap size={22} />
        </div>
        <div>
          <span className="brand-title">
            Source<span>2</span>Study
          </span>
        </div>
        <span className="brand-badge">v2.0 AI</span>
      </div>

      <nav className={`nav-tabs ${mobileMenuOpen ? 'mobile-open' : ''}`}>
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              className={`nav-tab ${isActive ? 'active' : ''}`}
              onClick={() => handleTabClick(tab.id)}
            >
              <Icon size={17} />
              <span>{tab.label}</span>
              {tab.badge > 0 && <span className="tab-badge">{tab.badge}</span>}
              {tab.highlight && !isActive && (
                <Sparkles size={13} style={{ color: '#818cf8', marginLeft: -2 }} />
              )}
            </button>
          );
        })}
      </nav>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div className="nav-status" title={isHealthy ? 'Backend Connected' : 'Connecting to API...'}>
          <span className={`status-dot ${isHealthy ? '' : 'offline'}`} />
          <span style={{ display: 'none', md: 'inline' }}>
            {isHealthy ? 'Online' : 'Offline'}
          </span>
        </div>

        <button
          className="mobile-menu-btn"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle navigation menu"
        >
          {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>
    </header>
  );
}
