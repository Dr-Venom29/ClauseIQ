import React, { useState } from 'react';
import axios from 'axios';

const RiskAnalysisView = ({ documentId }) => {
  const [risks, setRisks] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const analyzeRisks = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.post(`http://localhost:8000/api/v1/documents/${documentId}/risks`);
      setRisks(response.data);
    } catch (err) {
      setError('Failed to analyze risks.');
    } finally {
      setLoading(false);
    }
  };

  const renderRiskSection = (title, items, color) => {
    if (!items || items.length === 0) return null;
    return (
      <div style={{ marginBottom: '20px', borderLeft: `5px solid ${color}`, paddingLeft: '15px', textAlign: 'left' }}>
        <h3 style={{ color }}>{title}</h3>
        {items.map((item, idx) => (
          <div key={idx} style={{ marginBottom: '10px' }}>
            <strong>{item.risk}</strong>
            <p style={{ margin: '5px 0', fontSize: '0.95em' }}>{item.reason} <i>[{item.citation}]</i></p>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Risk Analysis</h2>
        <button onClick={analyzeRisks} disabled={loading} style={{ padding: '8px 16px' }}>
          {loading ? 'Analyzing...' : 'Analyze Risks'}
        </button>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {risks && (
        <div style={{ marginTop: '20px' }}>
          {renderRiskSection('High Risks', risks.high_risks, '#d32f2f')}
          {renderRiskSection('Medium Risks', risks.medium_risks, '#ed6c02')}
          {renderRiskSection('Low Risks', risks.low_risks, '#0288d1')}
          
          {risks.assumptions && risks.assumptions.length > 0 && (
            <div style={{ textAlign: 'left', marginTop: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '5px' }}>
              <h3>Assumptions Identified</h3>
              <ul>
                {risks.assumptions.map((assump, idx) => <li key={idx}>{assump}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}

      <div style={{ marginTop: '40px', fontSize: '0.85em', color: '#666', borderTop: '1px solid #ddd', paddingTop: '10px' }}>
        ClauseIQ provides AI-assisted research support only and does not constitute legal, tax, compliance, accounting, or professional advice.
      </div>
    </div>
  );
};

export default RiskAnalysisView;
