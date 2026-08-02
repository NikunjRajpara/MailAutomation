import React, { useState } from 'react';

export default function FilterSettings({ keywords, onKeywordsChange }) {
  const [newKw, setNewKw] = useState('');

  const handleAddKeyword = (e) => {
    e.preventDefault();
    const trimmed = newKw.trim().toLowerCase();
    if (trimmed && !keywords.includes(trimmed)) {
      const updated = [...keywords, trimmed];
      onKeywordsChange(updated);
      setNewKw('');
    }
  };

  const handleRemove = (kwToRemove) => {
    const updated = keywords.filter((kw) => kw !== kwToRemove);
    onKeywordsChange(updated);
  };

  const handleClearAll = () => {
    onKeywordsChange([]);
  };

  return (
    <div className="glass-card" style={{ marginTop: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#F8FAFC' }}>
          🛡️ Newsletter & Spam Filter Rules ({keywords.length} active)
        </h2>

        {keywords.length > 0 && (
          <button
            type="button"
            onClick={handleClearAll}
            style={{
              background: 'rgba(244, 63, 94, 0.15)',
              color: '#F43F5E',
              border: '1px solid rgba(244, 63, 94, 0.3)',
              borderRadius: '8px',
              padding: '4px 10px',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Clear All Tags (Process All Emails)
          </button>
        )}
      </div>

      <p style={{ fontSize: '13px', color: '#94A3B8', marginBottom: '16px' }}>
        Emails containing any of the active sender keywords below will be filtered out before AI processing. If you remove all tags, all unread emails will be processed.
      </p>

      <form onSubmit={handleAddKeyword} style={{ display: 'flex', gap: '10px', marginBottom: '18px' }}>
        <input
          type="text"
          placeholder="Add custom keyword/domain (e.g., deals@)"
          value={newKw}
          onChange={(e) => setNewKw(e.target.value)}
          className="form-input"
          style={{ flex: 1 }}
        />
        <button type="submit" className="btn btn-primary" style={{ padding: '10px 18px' }}>
          + Add
        </button>
      </form>

      {keywords.length === 0 ? (
        <div style={{ padding: '12px 16px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '10px', color: '#10B981', fontSize: '13px' }}>
          ✅ All filter tags removed! <strong>All unread emails will be ingested and summarized.</strong>
        </div>
      ) : (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {keywords.map((kw) => (
            <span
              key={kw}
              style={{
                background: 'rgba(99, 102, 241, 0.15)',
                color: '#818CF8',
                border: '1px solid rgba(99, 102, 241, 0.3)',
                borderRadius: '16px',
                padding: '4px 12px',
                fontSize: '12px',
                fontWeight: 500,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              {kw}
              <button
                type="button"
                onClick={() => handleRemove(kw)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#F43F5E',
                  cursor: 'pointer',
                  fontWeight: 700,
                  fontSize: '14px',
                }}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
