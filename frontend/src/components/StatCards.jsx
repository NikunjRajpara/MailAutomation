import React from 'react';

export default function StatCards({ stats, status }) {
  return (
    <div className="stats-grid">
      <div className="glass-card">
        <div className="stat-card-title">Target Recipient Email</div>
        <div className="stat-card-value" style={{ fontSize: '20px', color: '#6366F1' }}>
          {status?.user_email || 'user@example.com'}
        </div>
        <div className="stat-card-desc">Destination for daily briefing HTML dispatch</div>
      </div>

      <div className="glass-card">
        <div className="stat-card-title">Emails Processed (Last Run)</div>
        <div className="stat-card-value" style={{ color: '#10B981' }}>
          {stats?.total_processed ?? 0}
        </div>
        <div className="stat-card-desc">Relevant emails analyzed by Gemini AI</div>
      </div>

      <div className="glass-card">
        <div className="stat-card-title">Lookback Window</div>
        <div className="stat-card-value" style={{ color: '#06B6D4' }}>
          {status?.lookback_hours || 24} Hours
        </div>
        <div className="stat-card-desc">Query range for unread inbox messages</div>
      </div>

      <div className="glass-card">
        <div className="stat-card-title">Pipeline Mode</div>
        <div className="stat-card-value" style={{ fontSize: '22px', color: stats?.dry_run ? '#F59E0B' : '#10B981' }}>
          {stats?.dry_run ? 'DRY-RUN' : 'LIVE'}
        </div>
        <div className="stat-card-desc">
          {stats?.dry_run ? 'Simulation active (No emails sent)' : 'Live Gmail Dispatch Mode'}
        </div>
      </div>
    </div>
  );
}
