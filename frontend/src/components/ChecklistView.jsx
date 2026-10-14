import React, { useState } from 'react';
import axios from 'axios';

const ChecklistView = ({ documentId }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateChecklist = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.post(`http://localhost:8000/api/v1/documents/${documentId}/checklist`);
      setItems(response.data);
    } catch (err) {
      setError('Failed to generate checklist.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'present': return '#4caf50';
      case 'unclear': return '#ff9800';
      case 'missing': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Compliance Checklist</h2>
        <button onClick={generateChecklist} disabled={loading} style={{ padding: '8px 16px' }}>
          {loading ? 'Generating...' : 'Generate Checklist'}
        </button>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {items.length > 0 && (
        <table style={{ width: '100%', marginTop: '20px', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '2px solid #ddd' }}>
              <th style={{ padding: '10px' }}>Status</th>
              <th style={{ padding: '10px' }}>Requirement</th>
              <th style={{ padding: '10px' }}>Explanation</th>
              <th style={{ padding: '10px' }}>Citation</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '10px' }}>
                  <span style={{ 
                    backgroundColor: getStatusColor(item.status), 
                    color: 'white', 
                    padding: '4px 8px', 
                    borderRadius: '4px',
                    fontSize: '0.85em',
                    textTransform: 'uppercase'
                  }}>
                    {item.status}
                  </span>
                </td>
                <td style={{ padding: '10px', fontWeight: 'bold' }}>{item.title}</td>
                <td style={{ padding: '10px' }}>{item.explanation}</td>
                <td style={{ padding: '10px', color: '#666' }}>{item.citation}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div style={{ marginTop: '40px', fontSize: '0.85em', color: '#666', borderTop: '1px solid #ddd', paddingTop: '10px' }}>
        ClauseIQ provides AI-assisted research support only and does not constitute legal, tax, compliance, accounting, or professional advice.
      </div>
    </div>
  );
};

export default ChecklistView;
