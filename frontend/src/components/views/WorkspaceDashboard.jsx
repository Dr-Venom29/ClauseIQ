import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { 
  FileText, 
  Layers, 
  MessageSquare, 
  SplitSquareHorizontal, 
  Activity, 
  Clock, 
  ChevronRight, 
  Calendar,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import './views.css';

const WorkspaceDashboard = ({ setActiveRoute, onSelectDocument, setSelectedDocId }) => {
  const { currentUser } = useAuth();
  const [overview, setOverview] = useState({
    total_documents: 0,
    total_analyses: 0,
    total_chats: 0,
    total_comparisons: 0
  });
  const [activities, setActivities] = useState([]);
  const [recentDocs, setRecentDocs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Extract name from email
  const getDisplayName = () => {
    if (!currentUser?.email) return 'User';
    const parts = currentUser.email.split('@')[0];
    return parts.charAt(0).toUpperCase() + parts.slice(1);
  };

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // Get Overview metrics
        const overviewRes = await axios.get('http://localhost:8000/api/v1/dashboard/overview');
        setOverview(overviewRes.data);

        // Get Recent activities
        const activityRes = await axios.get('http://localhost:8000/api/v1/activity/recent');
        setActivities(activityRes.data);

        // Get Recent documents
        const docsRes = await axios.get('http://localhost:8000/api/v1/documents/my');
        // Sort documents by upload timestamp descending, take top 5
        const sortedDocs = [...docsRes.data].sort((a, b) => 
          new Date(b.upload_timestamp) - new Date(a.upload_timestamp)
        ).slice(0, 5);
        setRecentDocs(sortedDocs);

      } catch (err) {
        console.error("Error fetching dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const formatActivityAction = (act) => {
    const docName = act.document_name ? `"${act.document_name}"` : '';
    switch (act.action) {
      case 'upload':
        return `Uploaded document ${docName}`;
      case 'summary':
        return `Generated Executive Summary for ${docName}`;
      case 'checklist':
        return `Generated Compliance Checklist for ${docName}`;
      case 'risk_analysis':
        return `Analyzed Risk Profile for ${docName}`;
      case 'chat':
        return `Asked AI Chat query on ${docName}`;
      case 'comparison':
        return `Compared contract versions for ${docName}`;
      case 'export':
        return `Exported analysis report for ${docName}`;
      case 'delete':
        return `Deleted document ${docName}`;
      default:
        return `${act.action.charAt(0).toUpperCase() + act.action.slice(1)} action completed`;
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.08 }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    show: { y: 0, opacity: 1 }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem', padding: '1rem 0' }}>
      
      {/* Welcome Header */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(30, 30, 38, 0.4) 100%)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(99, 102, 241, 0.25)',
        borderRadius: 'var(--radius-xl)',
        padding: '2.5rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.15)'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--brand-primary)', marginBottom: '0.5rem' }}>
            <Sparkles size={16} />
            <span style={{ fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em' }}>Personal Workspace</span>
          </div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, letterSpacing: '-0.03em' }}>
            Welcome Back, {getDisplayName()}
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginTop: '0.5rem', maxWidth: '600px' }}>
            Analyze contracts, monitor compliance checklists, investigate contract risks, and run comparisons.
          </p>
        </div>
      </div>

      {/* Navigation Quick Actions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
        {[
          { label: 'My Documents', route: 'documents', count: overview.total_documents, icon: FileText, color: 'var(--brand-primary)' },
          { label: 'Analytics Dashboard', route: 'analytics', count: overview.total_analyses, icon: Activity, color: '#f59e0b' },
          { label: 'Compare Documents', route: 'compare', count: overview.total_comparisons, icon: SplitSquareHorizontal, color: '#10b981' },
          { label: 'Upload New Contract', route: 'upload', count: null, icon: Clock, color: '#6366f1' }
        ].map((act, idx) => (
          <div 
            key={idx}
            onClick={() => setActiveRoute(act.route)}
            style={{
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              borderRadius: 'var(--radius-lg)',
              padding: '1.5rem',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              height: '140px',
              transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
              position: 'relative',
              overflow: 'hidden'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)';
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.05)';
              e.currentTarget.style.transform = 'none';
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{
                width: '38px',
                height: '38px',
                borderRadius: '8px',
                background: `rgba(255, 255, 255, 0.03)`,
                border: '1px solid rgba(255, 255, 255, 0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: act.color
              }}>
                <act.icon size={20} />
              </div>
              <ChevronRight size={16} style={{ opacity: 0.4 }} />
            </div>

            <div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500 }}>{act.label}</div>
              {act.count !== null && (
                <div style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: '0.25rem' }}>{act.count}</div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Main Grid: Recent Documents and Activity Feed */}
      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="show"
        style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}
        className="dashboard-main-grid"
      >
        
        {/* Recent Documents Table Card */}
        <motion.div 
          variants={itemVariants}
          style={{
            background: 'linear-gradient(135deg, rgba(25, 25, 30, 0.4) 0%, rgba(15, 15, 20, 0.25) 100%)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
            borderRadius: 'var(--radius-xl)',
            padding: '1.75rem',
            boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.2)'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 650, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FileText size={18} style={{ color: 'var(--brand-primary)' }} />
              Recent Documents
            </h2>
            <span 
              onClick={() => setActiveRoute('documents')} 
              style={{ fontSize: '0.8rem', color: 'var(--brand-primary)', cursor: 'pointer', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}
            >
              All Documents <ArrowRight size={12} />
            </span>
          </div>

          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem 0', color: 'var(--text-secondary)' }}>Loading...</div>
          ) : recentDocs.length === 0 ? (
            <div style={{ padding: '3rem 0', textAlign: 'center', color: 'var(--text-muted)' }}>
              No documents uploaded yet. Upload a document to start analysis.
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)', color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Filename</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Version</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {recentDocs.map((doc) => (
                    <tr 
                      key={doc.id}
                      style={{ 
                        borderBottom: '1px solid rgba(255, 255, 255, 0.03)',
                        fontSize: '0.875rem',
                        transition: 'background-color 0.15s ease'
                      }}
                      onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.01)'}
                      onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    >
                      <td style={{ padding: '1rem', fontWeight: 500 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <FileText size={16} style={{ color: 'var(--brand-primary)', opacity: 0.8 }} />
                          <span 
                            onClick={() => {
                              onSelectDocument(doc);
                              setSelectedDocId(doc.id);
                              setActiveRoute('document-details');
                            }}
                            style={{ cursor: 'pointer', color: 'var(--text-primary)' }}
                          >
                            {doc.filename}
                          </span>
                        </div>
                      </td>
                      <td style={{ padding: '1rem' }}>
                        <span style={{ 
                          padding: '0.15rem 0.5rem', 
                          borderRadius: '4px', 
                          background: 'rgba(99, 102, 241, 0.08)', 
                          color: '#818cf8', 
                          fontSize: '0.7rem',
                          fontWeight: 600
                        }}>
                          v{doc.version_number}
                        </span>
                      </td>
                      <td style={{ padding: '1rem', textAlign: 'right' }}>
                        <button
                          onClick={() => {
                            onSelectDocument(doc);
                            setSelectedDocId(doc.id);
                            setActiveRoute('document-details');
                          }}
                          style={{
                            background: 'transparent',
                            border: '1px solid rgba(255, 255, 255, 0.06)',
                            color: 'var(--text-secondary)',
                            padding: '0.35rem 0.7rem',
                            borderRadius: 'var(--radius-md)',
                            fontSize: '0.75rem',
                            cursor: 'pointer',
                            fontWeight: 500
                          }}
                        >
                          Open Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>

        {/* Activity Feed Card */}
        <motion.div 
          variants={itemVariants}
          style={{
            background: 'linear-gradient(135deg, rgba(25, 25, 30, 0.4) 0%, rgba(15, 15, 20, 0.25) 100%)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
            borderRadius: 'var(--radius-xl)',
            padding: '1.75rem',
            boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.2)'
          }}
        >
          <h2 style={{ fontSize: '1.25rem', fontWeight: 650, display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
            <Clock size={18} style={{ color: '#f59e0b' }} />
            Recent Activity
          </h2>

          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem 0', color: 'var(--text-secondary)' }}>Loading...</div>
          ) : activities.length === 0 ? (
            <div style={{ padding: '3rem 0', textAlign: 'center', color: 'var(--text-muted)' }}>
              No operations logged yet.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: '380px', overflowY: 'auto', paddingRight: '0.25rem' }}>
              {activities.map((act, idx) => (
                <div 
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.75rem',
                    borderBottom: idx !== activities.length - 1 ? '1px solid rgba(255, 255, 255, 0.03)' : 'none',
                    paddingBottom: '0.75rem'
                  }}
                >
                  <div style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: '50%',
                    background: 'rgba(255,255,255,0.02)',
                    border: '1px solid rgba(255,255,255,0.05)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    marginTop: '0.15rem'
                  }}>
                    <Activity size={12} style={{ color: 'var(--brand-primary)' }} />
                  </div>
                  <div>
                    <p style={{ fontSize: '0.825rem', color: 'var(--text-primary)', lineHeight: 1.35 }}>
                      {formatActivityAction(act)}
                    </p>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginTop: '0.15rem' }}>
                      {new Date(act.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>

      </motion.div>

    </div>
  );
};

export default WorkspaceDashboard;
