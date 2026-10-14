import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Skeleton } from '../ui/Skeleton';
import { FileText, Anchor, BookOpen, ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';
import './views.css';

const SummaryView = ({ documentId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/v1/documents/${documentId}/summary`);
        setData(response.data);
      } catch (err) {
        console.error(err);
        setData({ error: "Failed to load summary." });
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, [documentId]);

  if (loading) return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <Skeleton style={{ height: '150px' }} />
      <Skeleton style={{ height: '100px' }} />
      <Skeleton style={{ height: '100px' }} />
    </div>
  );

  if (!data || data.error) return <div>{data?.error || "Error"}</div>;

  const containerVariants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.08 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <motion.div 
      variants={containerVariants} 
      initial="hidden" 
      animate="show" 
      style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}
    >
      {/* Executive Summary Card */}
      <motion.div variants={itemVariants} className="summary-card">
        <h3 className="summary-card-title">
          <FileText size={20} style={{ color: 'var(--text-primary)' }} />
          Executive Summary
        </h3>
        <p style={{ color: 'var(--text-primary)', fontSize: '0.975rem', lineHeight: '1.6', margin: 0 }}>
          {data.executive_summary}
        </p>
      </motion.div>

      {/* Purpose Card */}
      <motion.div variants={itemVariants} className="summary-card">
        <h3 className="summary-card-title">
          <Anchor size={20} style={{ color: 'var(--text-primary)' }} />
          Purpose
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.6', margin: 0 }}>
          {data.purpose}
        </p>
      </motion.div>

      {/* Grid for Key Obligations and Exceptions & Penalties */}
      <div className="summary-grid-obligations">
        {/* Key Obligations Card */}
        <motion.div variants={itemVariants} className="summary-card">
          <h3 className="summary-card-title">
            <BookOpen size={20} style={{ color: 'var(--text-primary)' }} />
            Key Obligations
          </h3>
          <ul className="summary-list">
            {data.key_obligations?.map((item, i) => (
              <li key={i} className="summary-list-item">
                <span className="summary-list-bullet"></span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </motion.div>

        {/* Exceptions & Penalties Card */}
        <motion.div variants={itemVariants} className="summary-card">
          <h3 className="summary-card-title">
            <ShieldAlert size={20} style={{ color: 'var(--status-warning)' }} />
            Exceptions & Penalties
          </h3>
          
          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.75rem', marginTop: 0 }}>
            Exceptions
          </h4>
          <ul className="summary-list" style={{ marginBottom: '1.5rem' }}>
            {data.exceptions?.map((item, i) => (
              <li key={i} className="summary-list-item">
                <span className="summary-list-bullet"></span>
                <span>{item}</span>
              </li>
            ))}
          </ul>

          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.75rem' }}>
            Penalties
          </h4>
          <ul className="summary-list">
            {data.penalties?.map((item, i) => (
              <li key={i} className="summary-list-item">
                <span className="summary-list-bullet"></span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </motion.div>
      </div>

    </motion.div>
  );
};

export default SummaryView;
