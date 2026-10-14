import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Skeleton } from '../ui/Skeleton';
import { ChevronDown, ChevronUp, FileText, Search } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './views.css';

const ClauseExplorer = ({ documentId }) => {
  const [clauses, setClauses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    const fetchClauses = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/v1/documents/${documentId}/clauses`);
        setClauses(response.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchClauses();
  }, [documentId]);

  if (loading) return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <Skeleton style={{ height: '60px' }} />
      <Skeleton style={{ height: '60px' }} />
      <Skeleton style={{ height: '60px' }} />
    </div>
  );

  const filteredClauses = clauses.filter(c => 
    c.title.toLowerCase().includes(search.toLowerCase()) || 
    c.content.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Premium Glassmorphic Search Bar */}
      <div className="clause-search-container">
        <input
          type="text"
          placeholder="Search clauses..."
          className="clause-search-input"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Search size={18} className="clause-search-icon" />
      </div>

      {/* Extracted Clauses Glass Cards List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {filteredClauses.map(clause => (
          <div key={clause.id} className="clause-card">
            <div 
              onClick={() => setExpandedId(expandedId === clause.id ? null : clause.id)}
              className={`clause-header ${expandedId === clause.id ? 'expanded' : ''}`}
            >
              <div className="clause-title-text">
                <FileText size={18} style={{ color: 'var(--text-secondary)' }} />
                <span>{clause.title}</span>
              </div>
              {expandedId === clause.id ? (
                <ChevronUp size={20} color="var(--text-muted)" />
              ) : (
                <ChevronDown size={20} color="var(--text-muted)" />
              )}
            </div>
            
            <AnimatePresence>
              {expandedId === clause.id && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.25, ease: 'easeInOut' }}
                  style={{ overflow: 'hidden' }}
                >
                  <div className="clause-expanded-content">
                    <p style={{ margin: 0, color: 'var(--text-secondary)' }}>
                      {clause.content}
                    </p>
                    <div className="clause-page-badge">
                      Source: Page {clause.page_number}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ))}
        {filteredClauses.length === 0 && (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            No clauses match your search.
          </div>
        )}
      </div>
    </div>
  );
};

export default ClauseExplorer;
