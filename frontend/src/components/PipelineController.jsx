import React, { useState } from 'react';

export default function PipelineController({ onTriggerBriefing, loading }) {
  const [hours, setHours] = useState(24);
  const [recipientEmail, setRecipientEmail] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onTriggerBriefing({
      dry_run: false,
      hours: Number(hours),
      recipient_email: recipientEmail.trim(),
    });
  };

  return (
    <div className="glass-card">
      <h2 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px', color: '#F8FAFC' }}>
        ⚡ Daily AI Briefing Dispatch
      </h2>

      <form onSubmit={handleSubmit}>
        <div className="form-group" style={{ marginBottom: '16px' }}>
          <label className="form-label">Recipient Email Address</label>
          <input
            type="email"
            placeholder="e.g., your.email@example.com"
            value={recipientEmail}
            onChange={(e) => setRecipientEmail(e.target.value)}
            className="form-input"
            required
            style={{ width: '100%' }}
          />
          <span style={{ fontSize: '12px', color: '#94A3B8', marginTop: '4px', display: 'block' }}>
            The rendered HTML Daily Briefing email will be dispatched live to this address.
          </span>
        </div>

        <div className="form-group" style={{ marginBottom: '16px' }}>
          <label className="form-label">Unread Lookback Window ({hours} Hours)</label>
          <input
            type="range"
            min="1"
            max="72"
            value={hours}
            onChange={(e) => setHours(e.target.value)}
            className="range-slider"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn btn-primary"
          style={{ width: '100%', marginTop: '8px', padding: '14px', fontSize: '15px' }}
        >
          {loading ? '⏳ Ingesting & Summarizing Inbox...' : '🚀 Generate & Dispatch Daily Briefing'}
        </button>
      </form>
    </div>
  );
}
