import React from 'react';

export default function Navbar({ status }) {
  return (
    <header className="glass-card navbar">
      <div className="nav-brand">
        <div className="logo-badge">🤖</div>
        <div className="nav-title">
          <h1>Gmail Briefing Bot Dashboard</h1>
          <div className="nav-subtitle">Google Workspace & Gemini AI Automated Intelligence</div>
        </div>
      </div>

      <div className="status-badges">
        <div className={`badge ${status?.has_credentials ? 'badge-success' : 'badge-warning'}`}>
          <span className="dot-indicator"></span>
          Gmail OAuth: {status?.has_credentials ? 'Connected' : 'Missing Credentials'}
        </div>

        <div className={`badge ${status?.has_gemini_key ? 'badge-purple' : 'badge-warning'}`}>
          <span className="dot-indicator"></span>
          AI Model: {status?.model || 'gemini-2.0-flash'}
        </div>
      </div>
    </header>
  );
}
