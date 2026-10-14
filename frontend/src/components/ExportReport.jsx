import React, { useState } from 'react';
import axios from 'axios';

const ExportReport = ({ documentId }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleExport = async () => {
    setLoading(true);
    setError('');
    try {
      // Create the export PDF
      const response = await axios.post(`http://localhost:8000/api/v1/documents/${documentId}/export`);
      const { download_url } = response.data;

      // Trigger download
      window.open(`http://localhost:8000${download_url}`, '_blank');
    } catch (err) {
      setError('Failed to export report.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <button 
        onClick={handleExport} 
        disabled={loading}
        style={{
          padding: '10px 20px',
          backgroundColor: '#4caf50',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          fontWeight: 'bold'
        }}
      >
        {loading ? 'Generating Report...' : 'Export PDF Report'}
      </button>
      {error && <span style={{ color: 'red', marginLeft: '10px' }}>{error}</span>}
    </div>
  );
};

export default ExportReport;
