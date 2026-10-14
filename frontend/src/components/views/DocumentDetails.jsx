import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/Tabs';
import SummaryView from './SummaryView';
import ChecklistView from './ChecklistView';
import RiskAnalysisView from './RiskAnalysisView';
import ChatView from './ChatView';
import ClauseExplorer from './ClauseExplorer';
import { FileText, Layers, Calendar, ChevronDown, History, ArrowRightLeft } from 'lucide-react';
import './views.css';

const DocumentDetails = ({ document, onSelectDocument, setActiveRoute }) => {
  const [versions, setVersions] = useState([]);
  const [showVersionMenu, setShowVersionMenu] = useState(false);

  useEffect(() => {
    if (!document) return;
    
    const fetchVersions = async () => {
      try {
        const res = await axios.get(`http://localhost:8000/api/v1/documents/${document.id}/versions`);
        // Sort topological
        const sorted = [...res.data].sort((a, b) => b.version_number - a.version_number);
        setVersions(sorted);
      } catch (err) {
        console.error("Error fetching version history:", err);
      }
    };

    fetchVersions();
  }, [document]);

  if (!document) return null;

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      
      {/* Premium Document Details Header */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(30, 30, 38, 0.4) 0%, rgba(20, 20, 25, 0.25) 100%)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.06)',
        borderRadius: 'var(--radius-xl)',
        padding: '1.75rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.2)',
        position: 'relative'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <FileText size={24} style={{ color: 'var(--brand-primary)' }} />
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0 }}>
              {document.filename}
            </h1>
            
            {/* Version Switcher Dropdown */}
            <div style={{ position: 'relative' }}>
              <button 
                onClick={() => setShowVersionMenu(!showVersionMenu)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  padding: '0.25rem 0.65rem',
                  borderRadius: '6px',
                  background: 'rgba(99, 102, 241, 0.08)',
                  border: '1px solid rgba(99, 102, 241, 0.15)',
                  color: '#818cf8',
                  fontSize: '0.775rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                <Layers size={12} />
                v{document.version_number}
                <ChevronDown size={12} />
              </button>

              {showVersionMenu && versions.length > 0 && (
                <div style={{
                  position: 'absolute',
                  top: '100%',
                  left: 0,
                  marginTop: '0.5rem',
                  background: 'rgba(25, 25, 30, 0.95)',
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: 'var(--radius-md)',
                  boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
                  zIndex: 100,
                  width: '200px',
                  overflow: 'hidden'
                }}>
                  <div style={{ padding: '0.5rem 0.75rem', fontSize: '0.7rem', color: 'var(--text-muted)', borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <History size={10} />
                    Version History
                  </div>
                  <div style={{ maxHeight: '180px', overflowY: 'auto' }}>
                    {versions.map((ver) => (
                      <div
                        key={ver.id}
                        onClick={() => {
                          onSelectDocument(ver);
                          setShowVersionMenu(false);
                        }}
                        style={{
                          padding: '0.6rem 0.75rem',
                          fontSize: '0.8rem',
                          cursor: 'pointer',
                          display: 'flex',
                          justifyContent: 'space-between',
                          background: ver.id === document.id ? 'rgba(255,255,255,0.02)' : 'transparent',
                          color: ver.id === document.id ? '#fff' : 'var(--text-secondary)'
                        }}
                        className="version-item"
                        onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.04)'}
                        onMouseOut={(e) => e.currentTarget.style.background = ver.id === document.id ? 'rgba(255,255,255,0.02)' : 'transparent'}
                      >
                        <span>v{ver.version_number}</span>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          {formatDate(ver.upload_timestamp)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.825rem' }}>
            <Calendar size={13} style={{ color: 'var(--text-muted)' }} />
            <span>Uploaded: {formatDate(document.upload_timestamp)}</span>
            <span>•</span>
            <span>ID: <code style={{ color: 'var(--text-muted)' }}>{document.id}</code></span>
          </div>
        </div>

        {/* Action Button for comparisons */}
        <button
          onClick={() => setActiveRoute('compare')}
          style={{
            background: 'rgba(99, 102, 241, 0.12)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            color: '#a5b4fc',
            padding: '0.5rem 1rem',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.825rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            transition: 'all 0.15s'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = 'var(--brand-primary)';
            e.currentTarget.style.color = '#fff';
            e.currentTarget.style.borderColor = 'var(--brand-primary)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = 'rgba(99, 102, 241, 0.12)';
            e.currentTarget.style.color = '#a5b4fc';
            e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.25)';
          }}
        >
          <ArrowRightLeft size={14} />
          Compare Version
        </button>
      </div>

      {/* Tabs Layout */}
      <Tabs defaultValue="summary" onValueChange={() => {}}>
        <TabsList>
          <TabsTrigger value="summary">Executive Summary</TabsTrigger>
          <TabsTrigger value="checklist">Compliance Checklist</TabsTrigger>
          <TabsTrigger value="risks">Risk Profile</TabsTrigger>
          <TabsTrigger value="chat">RAG Chat</TabsTrigger>
          <TabsTrigger value="clauses">Clause Explorer</TabsTrigger>
        </TabsList>
        
        <TabsContent value="summary"><SummaryView documentId={document.id} /></TabsContent>
        <TabsContent value="checklist"><ChecklistView documentId={document.id} /></TabsContent>
        <TabsContent value="risks"><RiskAnalysisView documentId={document.id} /></TabsContent>
        <TabsContent value="chat"><ChatView documentId={document.id} /></TabsContent>
        <TabsContent value="clauses"><ClauseExplorer documentId={document.id} /></TabsContent>
      </Tabs>

    </div>
  );
};

export default DocumentDetails;
