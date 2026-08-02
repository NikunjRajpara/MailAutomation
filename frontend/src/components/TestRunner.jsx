import React, { useState } from 'react';

export default function TestRunner() {
  const [running, setRunning] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const handleRunTests = async () => {
    setRunning(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/run-tests');
      const data = await res.json();
      setTestResult(data);
    } catch (err) {
      setTestResult({ passed: false, output: `API error: ${err.message}` });
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="glass-card" style={{ marginTop: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#F8FAFC' }}>
            🧪 Pytest Automated Test Runner
          </h2>
          <p style={{ fontSize: '12px', color: '#94A3B8' }}>
            Runs unit tests for HTML sanitization, newsletter filtering, AI prompt mocking, and MIME builders.
          </p>
        </div>

        <button
          onClick={handleRunTests}
          disabled={running}
          className="btn btn-secondary"
        >
          {running ? '⏳ Executing Pytest...' : '▶ Run Pytest Suite'}
        </button>
      </div>

      {testResult && (
        <div>
          <div
            className={`badge ${testResult.passed ? 'badge-success' : 'badge-warning'}`}
            style={{ marginBottom: '12px', fontSize: '13px' }}
          >
            {testResult.passed ? '✅ All 15 Pytest Units Passed (100%)' : '❌ Pytest Suite Returned Failures'}
          </div>

          <div className="terminal-box">
            <pre>{testResult.output}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
