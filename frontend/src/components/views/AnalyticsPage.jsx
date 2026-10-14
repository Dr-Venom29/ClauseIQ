import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { 
  UploadCloud, 
  MessageSquare, 
  SplitSquareHorizontal, 
  Download, 
  Cpu, 
  Database, 
  Percent, 
  TrendingUp,
  Activity,
  AlertCircle
} from 'lucide-react';
import { motion } from 'framer-motion';
import './views.css';

const AnalyticsPage = () => {
  const [metrics, setMetrics] = useState({
    uploads: 0,
    chats: 0,
    comparisons: 0,
    exports: 0,
    gemini_calls: 0,
    cache_hits: 0,
    cache_misses: 0,
    savings_percentage: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const res = await axios.get('http://localhost:8000/api/v1/metrics/user');
        setMetrics(res.data);
        setError('');
      } catch (err) {
        console.error("Error fetching user metrics:", err);
        setError('Failed to load metrics. Please refresh the page.');
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  const totalHitsAndMisses = metrics.cache_hits + metrics.cache_misses;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', padding: '1rem 0' }}>
      
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '2rem', fontWeight: 700, letterSpacing: '-0.03em' }}>
          Workspace Analytics & Observability
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.925rem', marginTop: '0.25rem' }}>
          Monitor AI operations volume, caching hit ratios, and cost savings across your portfolio.
        </p>
      </div>

      {error ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '2rem', background: 'rgba(239, 68, 68, 0.05)', border: '1px solid rgba(239, 68, 68, 0.1)', borderRadius: 'var(--radius-lg)', color: '#f87171' }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      ) : loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem 0', color: 'var(--text-secondary)' }}>
          Loading analysis metrics...
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          {/* Main Grid: Key Metrics & Savings */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.25fr 1fr', gap: '2rem' }} className="analytics-main-grid">
            
            {/* Efficiency & Savings Card */}
            <div style={{
              background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(20, 20, 25, 0.4) 100%)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(99, 102, 241, 0.2)',
              borderRadius: 'var(--radius-xl)',
              padding: '2rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.2)'
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--brand-primary)', marginBottom: '1rem' }}>
                  <TrendingUp size={16} />
                  <span style={{ fontSize: '0.75rem', fontWeight: 650, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Cost Optimization</span>
                </div>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Total API Savings</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '0.5rem', lineHeight: 1.45 }}>
                  ClauseIQ caches structural document analyses locally. Every cache hit represents a prompt bypass that would otherwise incur Gemini tokens, meaning faster load times and $0 additional API fees.
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '2rem', marginTop: '2rem' }}>
                <div style={{ position: 'relative', width: '120px', height: '120px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <svg style={{ transform: 'rotate(-90deg)', width: '120px', height: '120px' }}>
                    <circle 
                      cx="60" 
                      cy="60" 
                      r="50" 
                      style={{ fill: 'transparent', stroke: 'rgba(255,255,255,0.03)', strokeWidth: '10' }} 
                    />
                    <circle 
                      cx="60" 
                      cy="60" 
                      r="50" 
                      style={{ 
                        fill: 'transparent', 
                        stroke: 'var(--brand-primary)', 
                        strokeWidth: '10',
                        strokeDasharray: '314',
                        strokeDashoffset: 314 - (314 * metrics.savings_percentage) / 100,
                        transition: 'stroke-dashoffset 1s ease'
                      }} 
                    />
                  </svg>
                  <div style={{ position: 'absolute', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <span style={{ fontSize: '1.6rem', fontWeight: 800 }}>{metrics.savings_percentage}%</span>
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Saved</span>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Cache Efficiency Ratio</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.15rem' }}>
                      {metrics.cache_hits} / {totalHitsAndMisses} requests
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Active Outages Fallbacks Used</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#10b981', marginTop: '0.15rem' }}>
                      Heuristics Active
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Performance Indicators Grid */}
            <div style={{ display: 'grid', gridTemplateRows: 'repeat(3, 1fr)', gap: '1.25rem' }}>
              {[
                { title: 'AI Gateway Calls', value: metrics.gemini_calls, subtitle: 'Official Gemini 2.5 Requests', icon: Cpu, color: '#818cf8', bg: 'rgba(129, 140, 248, 0.05)' },
                { title: 'Local Cache Hits', value: metrics.cache_hits, subtitle: '$0 API Response snapshots reused', icon: Database, color: '#34d399', bg: 'rgba(52, 211, 153, 0.05)' },
                { title: 'Local Cache Misses', value: metrics.cache_misses, subtitle: 'First-time operations indexed', icon: AlertCircle, color: '#f87171', bg: 'rgba(248, 113, 113, 0.05)' }
              ].map((item, idx) => (
                <div 
                  key={idx}
                  style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    borderRadius: 'var(--radius-xl)',
                    padding: '1.25rem 1.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{
                      width: '42px',
                      height: '42px',
                      borderRadius: '10px',
                      background: item.bg,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: item.color
                    }}>
                      <item.icon size={20} />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>{item.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>{item.subtitle}</div>
                    </div>
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{item.value}</div>
                </div>
              ))}
            </div>

          </div>

          {/* Volume Statistics */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(25, 25, 30, 0.4) 0%, rgba(15, 15, 20, 0.25) 100%)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
            borderRadius: 'var(--radius-xl)',
            padding: '2rem',
            boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.25)'
          }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 650, display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '2rem' }}>
              <Activity size={18} style={{ color: 'var(--brand-primary)' }} />
              Workspace Volume Statistics
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '2rem' }}>
              {[
                { label: 'Contract Uploads', value: metrics.uploads, icon: UploadCloud, color: '#6366f1' },
                { label: 'Interactive Chats', value: metrics.chats, icon: MessageSquare, color: '#3b82f6' },
                { label: 'Version Comparisons', value: metrics.comparisons, icon: SplitSquareHorizontal, color: '#10b981' },
                { label: 'Report Exports', value: metrics.exports, icon: Download, color: '#ec4899' }
              ].map((stat, idx) => (
                <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    <stat.icon size={16} style={{ color: stat.color }} />
                    {stat.label}
                  </div>
                  <div style={{ fontSize: '2rem', fontWeight: 800 }}>{stat.value}</div>
                  <div style={{ height: '4px', borderRadius: '2px', background: 'rgba(255,255,255,0.03)', position: 'relative', overflow: 'hidden' }}>
                    <div style={{
                      height: '100%',
                      background: stat.color,
                      width: `${Math.min((stat.value / (Math.max(metrics.uploads, metrics.chats, metrics.comparisons, metrics.exports, 1)) * 100), 100)}%`,
                      borderRadius: '2px'
                    }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

    </div>
  );
};

export default AnalyticsPage;
