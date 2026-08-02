import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import StatCards from './components/StatCards';
import PipelineController from './components/PipelineController';
import BriefingPreview from './components/BriefingPreview';
import FilterSettings from './components/FilterSettings';

export default function App() {
  const [status, setStatus] = useState(null);
  const [briefingStats, setBriefingStats] = useState(null);
  const [briefingPreview, setBriefingPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filterKeywords, setFilterKeywords] = useState([
    "noreply", "no-reply", "newsletter", "marketing", "promotions",
    "notifications", "updates", "digest", "info@", "news@", "bounce", "alert"
  ]);

  const API_BASE = 'http://127.0.0.1:8000';

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/status`);
      const data = await res.json();
      setStatus(data);
    } catch (err) {
      console.warn('Backend API offline or unreachable:', err);
    }
  };

  const fetchPreview = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/preview`);
      const data = await res.json();
      setBriefingPreview(data);
    } catch (err) {
      console.warn('Failed to fetch briefing preview:', err);
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchPreview();
  }, []);

  const handleTriggerBriefing = async (payload) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/run-briefing`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...payload,
          custom_keywords: filterKeywords,
        }),
      });
      const data = await res.json();
      if (data.success) {
        setBriefingStats(data.metrics);
        setBriefingPreview({
          html: data.preview_html,
          plain: data.preview_plain,
        });
        fetchStatus();
      }
    } catch (err) {
      alert(`Error triggering briefing: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Navbar status={status} />

      <StatCards stats={briefingStats} status={status} />

      <div className="dashboard-grid">
        <div>
          <PipelineController
            onTriggerBriefing={handleTriggerBriefing}
            loading={loading}
          />
          <FilterSettings
            keywords={filterKeywords}
            onKeywordsChange={setFilterKeywords}
          />
        </div>

        <div>
          <BriefingPreview briefingData={briefingPreview} />
        </div>
      </div>
    </div>
  );
}
