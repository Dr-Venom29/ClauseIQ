import React, { useEffect, useState, useRef } from 'react';
import { FileText, Layers, AlertTriangle, CheckCircle, ShieldCheck, Database, HelpCircle } from 'lucide-react';
import axios from 'axios';
import gsap from 'gsap';
import './views.css';

const Overview = ({ document }) => {
  const [metrics, setMetrics] = useState(null);
  const headerRef = useRef(null);
  const cardsRef = useRef([]);

  useEffect(() => {
    axios.get('http://localhost:8000/api/v1/metrics').then(res => {
      setMetrics(res.data);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    // Premium GSAP animation sequence
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
    
    tl.fromTo(headerRef.current, 
      { opacity: 0, y: -15 }, 
      { opacity: 1, y: 0, duration: 0.6 }
    )
    .fromTo(cardsRef.current,
      { opacity: 0, y: 15 },
      { opacity: 1, y: 0, duration: 0.5, stagger: 0.08 },
      "-=0.3"
    );
  }, [document]);

  if (!document) return null;

  const totalCacheHits = metrics?.metrics?.cache_hit || 0;

  return (
    <div className="overview-container">
      {/* Premium Document Header Card */}
      <div className="document-header-card" ref={headerRef}>
        <div className="document-title-area">
          <h1 className="document-filename">
            <FileText size={28} style={{ color: 'var(--text-primary)' }} />
            {document.filename}
            <span style={{ fontSize: '0.875rem', fontWeight: 500, opacity: 0.6, background: 'rgba(255,255,255,0.06)', padding: '0.25rem 0.5rem', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.08)' }}>
              v{document.version_number}
            </span>
          </h1>
          <div className="document-metadata">
            <span>ID: <code style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{document.id}</code></span>
            <span>•</span>
            <span>Uploaded: {new Date(document.upload_timestamp).toLocaleDateString()}</span>
          </div>
        </div>
        <div className="document-status-badge">
          <ShieldCheck size={18} />
          Processed Successfully
        </div>
      </div>

      <div className="overview-section-title">
        <HelpCircle size={18} style={{ color: 'var(--text-muted)' }} />
        Document Intelligence Overview
      </div>
      
      {/* Premium Glassmorphic Grid */}
      <div className="overview-grid">
        <div 
          className="metric-card info" 
          ref={el => cardsRef.current[0] = el}
        >
          <div className="metric-header">
            <span className="metric-title">Total Clauses Extracted</span>
            <div className="metric-icon-box">
              <Layers size={18} />
            </div>
          </div>
          <div className="metric-body">
            <h2 className="metric-value">24</h2>
          </div>
        </div>
        
        <div 
          className="metric-card danger" 
          ref={el => cardsRef.current[1] = el}
        >
          <div className="metric-header">
            <span className="metric-title">High Risks Detected</span>
            <div className="metric-icon-box">
              <AlertTriangle size={18} />
            </div>
          </div>
          <div className="metric-body">
            <h2 className="metric-value" style={{ color: 'var(--status-danger)' }}>3</h2>
          </div>
        </div>

        <div 
          className="metric-card success" 
          ref={el => cardsRef.current[2] = el}
        >
          <div className="metric-header">
            <span className="metric-title">Compliance Score</span>
            <div className="metric-icon-box">
              <CheckCircle size={18} />
            </div>
          </div>
          <div className="metric-body">
            <h2 className="metric-value" style={{ color: 'var(--status-success)' }}>85%</h2>
          </div>
        </div>

        <div 
          className="metric-card info" 
          ref={el => cardsRef.current[3] = el}
        >
          <div className="metric-header">
            <span className="metric-title">Global Cache Hits</span>
            <div className="metric-icon-box">
              <Database size={18} />
            </div>
          </div>
          <div className="metric-body">
            <h2 className="metric-value">{totalCacheHits}</h2>
          </div>
        </div>
      </div>
      
      {/* Ready for Analysis Card */}
      <div className="ready-analysis-card" ref={el => cardsRef.current[4] = el}>
        <div className="ready-title">Ready for Analysis</div>
        <p className="ready-desc">
          Navigate using the tabs below to explore the detailed executive summary, 
          compliance checklists, risk profiles, or run instant document-scoped RAG chat queries.
        </p>
      </div>
    </div>
  );
};

export default Overview;
