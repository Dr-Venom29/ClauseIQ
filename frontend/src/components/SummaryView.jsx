import React, { useState } from 'react';
import axios from 'axios';

const SummaryView = ({ documentId }) => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateSummary = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.post(`http://localhost:8000/api/v1/documents/${documentId}/summary`);
      setSummary(response.data);
    } catch (err) {
      setError('Failed to generate summary.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Document Summary</h2>
        <button onClick={generateSummary} disabled={loading} style={{ padding: '8px 16px' }}>
          {loading ? 'Generating...' : 'Generate Summary'}
        </button>
      </div>
      
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {summary && (
        <div style={{ marginTop: '20px', textAlign: 'left' }}>
          <h3>Executive Summary</h3>
          <p>{summary.executive_summary}</p>
          
          <h3>Purpose of Document</h3>
          <p>{summary.purpose}</p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <h3>Key Obligations</h3>
              <ul>{summary.key_obligations?.map((item, i) => <li key={i}>{item}</li>)}</ul>
            </div>
            <div>
              <h3>Important Clauses</h3>
              <ul>{summary.important_clauses?.map((item, i) => <li key={i}>{item}</li>)}</ul>
            </div>
            <div>
              <h3>Penalties</h3>
              <ul>{summary.penalties?.map((item, i) => <li key={i}>{item}</li>)}</ul>
            </div>
            <div>
              <h3>Exceptions</h3>
              <ul>{summary.exceptions?.map((item, i) => <li key={i}>{item}</li>)}</ul>
            </div>
          </div>
          
          <h3>Final Takeaways</h3>
          <ul>{summary.takeaways?.map((item, i) => <li key={i}>{item}</li>)}</ul>
        </div>
      )}

      <div style={{ marginTop: '40px', fontSize: '0.85em', color: '#666', borderTop: '1px solid #ddd', paddingTop: '10px' }}>
        ClauseIQ provides AI-assisted research support only and does not constitute legal, tax, compliance, accounting, or professional advice.
      </div>
    </div>
  );
};

export default SummaryView;
