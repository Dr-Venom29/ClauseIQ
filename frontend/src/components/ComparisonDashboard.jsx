import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ComparisonDashboard = ({ docAId, docBId, onBack }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [exporting, setExporting] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        const response = await axios.post('http://localhost:8000/api/v1/compare', {
          doc_a_id: docAId,
          doc_b_id: docBId
        });
        setData(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to compare documents');
      } finally {
        setLoading(false);
      }
    };
    fetchComparison();
  }, [docAId, docBId]);

  const handleExport = async () => {
    setExporting(true);
    try {
      const response = await axios.post('http://localhost:8000/api/v1/export/comparison', {
        doc_a_id: docAId,
        doc_b_id: docBId
      });
      window.open(`http://localhost:8000${response.data.download_url}`, '_blank');
    } catch (err) {
      alert('Failed to export report');
    } finally {
      setExporting(false);
    }
  };

  if (loading) return <div>Analyzing semantic differences and risk impacts... This may take a minute.</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;
  if (!data) return <div>No data available</div>;

  const { comparison_result, risk_delta, compliance_impact } = data;

  const tabStyle = (tabName) => ({
    padding: '10px 20px', cursor: 'pointer',
    backgroundColor: activeTab === tabName ? '#d32f2f' : '#f0f0f0',
    color: activeTab === tabName ? 'white' : 'black',
    border: 'none', marginRight: '10px', borderRadius: '5px'
  });

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h2>Version Comparison</h2>
        <div>
          <button onClick={onBack} style={{ padding: '8px 16px', marginRight: '10px' }}>Back to Dashboard</button>
          <button onClick={handleExport} disabled={exporting} style={{ padding: '8px 16px', backgroundColor: '#4caf50', color: 'white', border: 'none', borderRadius: '4px' }}>
            {exporting ? 'Generating...' : 'Export Comparison PDF'}
          </button>
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <button style={tabStyle('overview')} onClick={() => setActiveTab('overview')}>Overview</button>
        <button style={tabStyle('changes')} onClick={() => setActiveTab('changes')}>Detailed Changes</button>
        <button style={tabStyle('risks')} onClick={() => setActiveTab('risks')}>Risk Impact</button>
      </div>

      <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '8px', minHeight: '400px', textAlign: 'left' }}>
        {activeTab === 'overview' && (
          <div>
            <h3>Changes Summary</h3>
            <ul>
              <li><strong>Added Clauses:</strong> {comparison_result.added.length}</li>
              <li><strong>Removed Clauses:</strong> {comparison_result.removed.length}</li>
              <li><strong>Modified Clauses:</strong> {comparison_result.modified.length}</li>
              <li><strong>Unchanged Clauses:</strong> {comparison_result.unchanged.length}</li>
            </ul>
          </div>
        )}

        {activeTab === 'changes' && (
          <div>
            <h3>Modified Clauses</h3>
            {comparison_result.modified.length === 0 ? <p>No clauses were modified.</p> : comparison_result.modified.map((m, i) => (
              <div key={i} style={{ marginBottom: '30px', padding: '15px', borderLeft: '4px solid #ff9800', backgroundColor: '#fff8e1' }}>
                <h4>{m.old_clause.clause_id} - {m.old_clause.title}</h4>
                <div style={{ display: 'flex', gap: '20px', fontSize: '0.9em' }}>
                  <div style={{ flex: 1, color: '#d32f2f' }}><del>{m.old_clause.content}</del></div>
                  <div style={{ flex: 1, color: '#2e7d32' }}><ins>{m.new_clause.content}</ins></div>
                </div>
                <div style={{ marginTop: '15px', backgroundColor: 'white', padding: '10px', borderRadius: '4px' }}>
                  <strong>AI Analysis:</strong> {m.analysis.what_changed}<br/>
                  <strong>Compliance Impact:</strong> {m.analysis.compliance_impact}
                </div>
              </div>
            ))}

            <h3>Added Clauses</h3>
            {comparison_result.added.map((a, i) => (
              <div key={i} style={{ marginBottom: '15px', padding: '10px', borderLeft: '4px solid #4caf50', backgroundColor: '#e8f5e9' }}>
                <h4>{a.clause_id} - {a.title}</h4>
                <p>{a.content}</p>
              </div>
            ))}

            <h3>Removed Clauses</h3>
            {comparison_result.removed.map((r, i) => (
              <div key={i} style={{ marginBottom: '15px', padding: '10px', borderLeft: '4px solid #f44336', backgroundColor: '#ffebee' }}>
                <h4>{r.clause_id} - {r.title}</h4>
                <p>{r.content}</p>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'risks' && (
          <div>
            <h3 style={{ color: '#d32f2f' }}>Risk Increased</h3>
            <ul>{risk_delta.risk_increased.map((r, i) => <li key={i}>{r}</li>)}</ul>
            
            <h3 style={{ color: '#2e7d32' }}>Risk Decreased</h3>
            <ul>{risk_delta.risk_decreased.map((r, i) => <li key={i}>{r}</li>)}</ul>

            <h3 style={{ color: '#ed6c02' }}>New Risks</h3>
            <ul>{risk_delta.new_risks.map((r, i) => <li key={i}>{r}</li>)}</ul>
          </div>
        )}
      </div>
      <div style={{ marginTop: '40px', fontSize: '0.85em', color: '#666', borderTop: '1px solid #ddd', paddingTop: '10px' }}>
        ClauseIQ provides AI-assisted research support only and does not constitute legal, tax, compliance, accounting, or professional advice.
      </div>
    </div>
  );
};

export default ComparisonDashboard;
