import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Badge } from '../ui/Badge';
import { Skeleton } from '../ui/Skeleton';
import { motion } from 'framer-motion';
import { CheckCircle2, AlertCircle, HelpCircle } from 'lucide-react';
import './views.css';

const ChecklistView = ({ documentId }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('All');

  useEffect(() => {
    const fetchChecklist = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/v1/documents/${documentId}/checklist`);
        setItems(response.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchChecklist();
  }, [documentId]);

  if (loading) return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <Skeleton style={{ height: '40px' }} />
      <Skeleton style={{ height: '60px' }} />
      <Skeleton style={{ height: '60px' }} />
      <Skeleton style={{ height: '60px' }} />
    </div>
  );

  const filteredItems = items.filter(item => filter === 'All' || item.status.toLowerCase() === filter.toLowerCase());

  const getStatusIcon = (status) => {
    switch(status.toLowerCase()) {
      case 'present': return <CheckCircle2 color="var(--status-success)" size={18} />;
      case 'missing': return <AlertCircle color="var(--status-danger)" size={18} />;
      default: return <HelpCircle color="var(--status-warning)" size={18} />;
    }
  };

  const getStatusBadge = (status) => {
    switch(status.toLowerCase()) {
      case 'present': return <Badge variant="success" style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem' }}>Present</Badge>;
      case 'missing': return <Badge variant="danger" style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem' }}>Missing</Badge>;
      default: return <Badge variant="warning" style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem' }}>Unclear</Badge>;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Premium Tab Filters */}
      <div className="filter-button-group">
        {['All', 'Present', 'Missing', 'Unclear'].map(f => (
          <button 
            key={f} 
            onClick={() => setFilter(f)}
            className={`filter-button ${filter === f ? 'active' : ''}`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Premium Glassmorphic Table Card */}
      <div className="checklist-table-card">
        <div style={{ overflowX: 'auto' }}>
          <table className="checklist-table">
            <thead>
              <tr>
                <th style={{ width: '25%' }}>Requirement</th>
                <th style={{ width: '12%' }}>Status</th>
                <th style={{ width: '38%' }}>Explanation</th>
                <th style={{ width: '25%' }}>Evidence</th>
              </tr>
            </thead>
            <tbody>
              {filteredItems.map((item, idx) => (
                <motion.tr 
                  key={idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.04 }}
                >
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {getStatusIcon(item.status)}
                      {item.title}
                    </div>
                  </td>
                  <td>{getStatusBadge(item.status)}</td>
                  <td style={{ color: 'var(--text-secondary)' }}>{item.explanation}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontStyle: 'italic' }}>
                    {item.citation !== 'None' ? `"${item.citation}"` : '-'}
                  </td>
                </motion.tr>
              ))}
              {filteredItems.length === 0 && (
                <tr>
                  <td colSpan="4" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No requirements match the selected filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ChecklistView;
