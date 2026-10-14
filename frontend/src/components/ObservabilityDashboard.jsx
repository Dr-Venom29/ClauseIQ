import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ObservabilityDashboard = ({ onClose }) => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/v1/metrics');
        setMetrics(response.data);
      } catch (err) {
        console.error("Failed to load metrics", err);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Loading Metrics...</div>;
  if (!metrics) return <div>Error loading metrics.</div>;

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.8)', color: 'white', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
      <div style={{ backgroundColor: '#242424', padding: '30px', borderRadius: '10px', width: '80%', maxWidth: '600px', position: 'relative' }}>
        <button onClick={onClose} style={{ position: 'absolute', top: '10px', right: '10px', background: 'transparent', border: 'none', color: 'white', fontSize: '20px', cursor: 'pointer' }}>×</button>
        <h2 style={{ marginTop: 0 }}>System Observability & Costs</h2>
        
        <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
          <div style={{ flex: 1, backgroundColor: '#1a1a1a', padding: '20px', borderRadius: '8px', textAlign: 'center' }}>
            <h3 style={{ margin: 0, color: '#888' }}>Gemini Calls</h3>
            <p style={{ fontSize: '36px', margin: '10px 0', fontWeight: 'bold' }}>{metrics.metrics.gemini_call}</p>
          </div>
          <div style={{ flex: 1, backgroundColor: '#1a1a1a', padding: '20px', borderRadius: '8px', textAlign: 'center' }}>
            <h3 style={{ margin: 0, color: '#888' }}>Cache Hits</h3>
            <p style={{ fontSize: '36px', margin: '10px 0', fontWeight: 'bold', color: '#4caf50' }}>{metrics.metrics.cache_hit}</p>
          </div>
          <div style={{ flex: 1, backgroundColor: '#1a1a1a', padding: '20px', borderRadius: '8px', textAlign: 'center' }}>
            <h3 style={{ margin: 0, color: '#888' }}>API Savings</h3>
            <p style={{ fontSize: '36px', margin: '10px 0', fontWeight: 'bold', color: '#2196f3' }}>{metrics.api_savings_percentage}%</p>
          </div>
        </div>

        <div>
          <h3 style={{ color: '#888', borderBottom: '1px solid #333', paddingBottom: '10px' }}>Detailed Operations</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #333' }}>
              <span>Total Uploads</span>
              <span>{metrics.metrics.upload}</span>
            </li>
            <li style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #333' }}>
              <span>Total Chat Queries</span>
              <span>{metrics.metrics.chat}</span>
            </li>
            <li style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #333' }}>
              <span>Cache Misses (LLM Required)</span>
              <span>{metrics.metrics.cache_miss}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ObservabilityDashboard;
