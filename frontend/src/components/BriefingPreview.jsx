import React from 'react';

export default function BriefingPreview({ briefingData }) {
  const htmlContent = briefingData?.html || '<p style="padding: 24px; color: #64748B; font-family: sans-serif;">No briefing preview available yet. Click <strong>Generate & Dispatch Daily Briefing</strong> to trigger live processing.</p>';

  return (
    <div className="glass-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#F8FAFC' }}>
          📄 Live Daily Briefing Email Preview
        </h2>
        <span style={{ fontSize: '12px', color: '#10B981', fontWeight: 600 }}>
          Rendered HTML View
        </span>
      </div>

      <iframe
        title="Daily Briefing Rendered Preview"
        srcDoc={htmlContent}
        className="preview-frame"
      />
    </div>
  );
}
