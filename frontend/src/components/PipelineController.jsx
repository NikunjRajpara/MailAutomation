import React, { useState } from 'react';

export default function PipelineController({ onTriggerBriefing, loading }) {
  const [hours, setHours] = useState(24);

  const handleSubmit = (e) => {
    e.preventDefault();
    onTriggerBriefing({
      dry_run: false,
      hours: Number(hours),
    });
  };

  return (
    <div className="glass-card">
      <h2 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px', color: '#F8FAFC' }}>
        ⚡ Daily AI Briefing Dispatch
      </h2>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
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
          style={{ width: '100%', marginTop: '16px', padding: '14px', fontSize: '15px' }}
        >
          {loading ? '⏳ Ingesting & Summarizing Inbox...' : '🚀 Generate & Dispatch Daily Briefing'}
        </button>
      </form>
    </div>
  );
}
