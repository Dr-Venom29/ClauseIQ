import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Skeleton } from '../ui/Skeleton';
import { Badge } from '../ui/Badge';
import { AlertTriangle, AlertCircle, Info } from 'lucide-react';
import { motion } from 'framer-motion';
import './views.css';

const RiskAnalysisView = ({ documentId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRisks = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/v1/documents/${documentId}/risks`);
        setData(response.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRisks();
  }, [documentId]);

  if (loading) return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <Skeleton style={{ height: '100px' }} />
      <Skeleton style={{ height: '100px' }} />
    </div>
  );

  const RiskCard = ({ risk, level }) => {
    let Icon = Info;
    if (level === 'high') Icon = AlertTriangle;
    if (level === 'medium') Icon = AlertCircle;

    return (
      <div className={`risk-item-card ${level}`}>
        <div className="risk-card-header">
          <div className="risk-title">
            <Icon size={18} />
            <span>{risk.risk}</span>
          </div>
          <Badge 
            variant={level === 'high' ? 'danger' : level === 'medium' ? 'warning' : 'outline'}
            style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem' }}
          >
            {level.toUpperCase()}
          </Badge>
        </div>
        <p className="risk-reason">{risk.reason}</p>
        {risk.citation && risk.citation !== 'None' && (
          <div className="risk-citation">
            "{risk.citation}"
          </div>
        )}
      </div>
    );
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}
    >
      {/* High Risks Section */}
      <div className="risk-section">
        <h2 className="risk-level-title high">
          <AlertTriangle size={20} /> High Risks ({data?.high_risks?.length || 0})
        </h2>
        {data?.high_risks?.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontStyle: 'italic', margin: 0, paddingLeft: '0.5rem' }}>
            No high risks detected in this document.
          </p>
        ) : (
          data?.high_risks?.map((r, i) => <RiskCard key={`h-${i}`} risk={r} level="high" />)
        )}
      </div>

      {/* Medium Risks Section */}
      <div className="risk-section">
        <h2 className="risk-level-title medium">
          <AlertCircle size={20} /> Medium Risks ({data?.medium_risks?.length || 0})
        </h2>
        {data?.medium_risks?.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontStyle: 'italic', margin: 0, paddingLeft: '0.5rem' }}>
            No medium risks detected.
          </p>
        ) : (
          data?.medium_risks?.map((r, i) => <RiskCard key={`m-${i}`} risk={r} level="medium" />)
        )}
      </div>

      {/* Low Risks Section */}
      <div className="risk-section">
        <h2 className="risk-level-title low">
          <Info size={20} /> Low Risks/Notables ({data?.low_risks?.length || 0})
        </h2>
        {data?.low_risks?.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontStyle: 'italic', margin: 0, paddingLeft: '0.5rem' }}>
            No low risks detected.
          </p>
        ) : (
          data?.low_risks?.map((r, i) => <RiskCard key={`l-${i}`} risk={r} level="low" />)
        )}
      </div>

    </motion.div>
  );
};

export default RiskAnalysisView;
