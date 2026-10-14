import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  FileText, 
  UploadCloud, 
  Loader2, 
  Plus, 
  Calendar, 
  Layers, 
  Search, 
  ArrowRight, 
  AlertCircle, 
  History,
  FileCheck
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '../ui/Button';
import './views.css';

const MyDocuments = ({ onSelectDocument }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [versionTarget, setVersionTarget] = useState(null); // Document to upload a version for
  const [activeDropdown, setActiveDropdown] = useState(null);
  
  const fileInputRef = useRef(null);
  const versionFileInputRef = useRef(null);

  useEffect(() => {
    const handleOutsideClick = () => setActiveDropdown(null);
    window.addEventListener('click', handleOutsideClick);
    return () => window.removeEventListener('click', handleOutsideClick);
  }, []);

  const handleDeleteDocument = async (docId) => {
    if (!window.confirm("Are you sure you want to permanently delete this document, its version history, analysis snapshots, and FAISS vectors?")) {
      return;
    }
    try {
      await axios.delete(`http://localhost:8000/api/v1/documents/${docId}`);
      fetchDocuments();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to delete document.");
    }
  };

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const res = await axios.get('http://localhost:8000/api/v1/documents/my');
      setDocuments(res.data);
      setError('');
    } catch (err) {
      console.error(err);
      setError('Failed to load documents. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleVersionFileSelect = (e) => {
    if (e.target.files && e.target.files[0] && versionTarget) {
      handleVersionUpload(e.target.files[0], versionTarget);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file.name.endsWith('.pdf')) {
      alert('Only PDF files are supported.');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:8000/api/v1/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // Refresh documents
      await fetchDocuments();
      // Automatically select and enter dashboard
      onSelectDocument(res.data);
    } catch (err) {
      console.error(err);
      alert('Failed to upload document.');
    } finally {
      setUploading(false);
    }
  };

  const handleVersionUpload = async (file, parentDoc) => {
    if (!file.name.endsWith('.pdf')) {
      alert('Only PDF files are supported.');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(`http://localhost:8000/api/v1/documents/${parentDoc.id}/version`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setVersionTarget(null);
      await fetchDocuments();
      onSelectDocument(res.data);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || 'Failed to upload new version.');
    } finally {
      setUploading(false);
    }
  };

  const filteredDocs = documents.filter(doc => 
    doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', padding: '1rem 0' }}>
      
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 700, letterSpacing: '-0.03em', color: 'var(--text-primary)' }}>
            My Documents
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.925rem', marginTop: '0.25rem' }}>
            Manage and analyze your legal agreements, NDAs, and contract versions.
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>
        
        {/* Top/Left upload zone */}
        <div 
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{
            background: 'linear-gradient(135deg, rgba(30, 30, 38, 0.4) 0%, rgba(20, 20, 25, 0.25) 100%)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            border: isDragging ? '2px dashed var(--brand-primary)' : '1px dashed rgba(255, 255, 255, 0.15)',
            borderRadius: 'var(--radius-xl)',
            padding: '3rem 2rem',
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.2)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '1.25rem',
            position: 'relative',
            overflow: 'hidden'
          }}
          className="upload-card"
        >
          {/* Subtle glowing element */}
          <div style={{
            position: 'absolute',
            width: '150px',
            height: '150px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0) 70%)',
            top: '-50px',
            right: '-50px',
            pointerEvents: 'none'
          }} />

          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileSelect} 
            accept=".pdf" 
            style={{ display: 'none' }} 
          />

          <input 
            type="file" 
            ref={versionFileInputRef} 
            onChange={handleVersionFileSelect} 
            accept=".pdf" 
            style={{ display: 'none' }} 
          />

          {uploading ? (
            <>
              <div style={{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                background: 'rgba(99, 102, 241, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Loader2 className="animate-spin" size={30} style={{ color: 'var(--brand-primary)' }} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Processing Document...</h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                  Extracting sections, indexing embeddings, and generating compliance checklist.
                </p>
              </div>
            </>
          ) : (
            <>
              <div style={{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid rgba(255, 255, 255, 0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--text-secondary)',
                transition: 'all 0.3s'
              }} className="icon-container">
                <UploadCloud size={30} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Upload New Document
                </h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                  Drag & drop your agreement PDF here, or <span style={{ color: 'var(--brand-primary)', fontWeight: 500 }}>browse files</span>
                </p>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                  Supported formats: PDF (Max 15MB)
                </p>
              </div>
            </>
          )}
        </div>

        {/* Document List */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(25, 25, 30, 0.4) 0%, rgba(15, 15, 20, 0.25) 100%)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          borderRadius: 'var(--radius-xl)',
          padding: '1.5rem',
          boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.25)'
        }}>
          
          {/* List Header / Search Bar */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '1.5rem',
            gap: '1.5rem',
            flexWrap: 'wrap'
          }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FileCheck size={18} style={{ color: 'var(--brand-primary)' }} />
              Documents Archive ({filteredDocs.length})
            </h2>

            <div style={{
              position: 'relative',
              maxWidth: '300px',
              width: '100%'
            }}>
              <Search size={16} style={{
                position: 'absolute',
                left: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-muted)'
              }} />
              <input
                type="text"
                placeholder="Search documents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  width: '100%',
                  background: 'rgba(0, 0, 0, 0.2)',
                  border: '1px solid rgba(255, 255, 255, 0.05)',
                  borderRadius: 'var(--radius-md)',
                  padding: '0.5rem 1rem 0.5rem 2.25rem',
                  color: 'var(--text-primary)',
                  fontSize: '0.875rem',
                  outline: 'none',
                  transition: 'all 0.2s'
                }}
                onFocus={(e) => e.target.style.borderColor = 'rgba(99, 102, 241, 0.4)'}
                onBlur={(e) => e.target.style.borderColor = 'rgba(255, 255, 255, 0.05)'}
              />
            </div>
          </div>

          {/* Table Container */}
          {loading ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem 0', gap: '1rem' }}>
              <Loader2 className="animate-spin" size={24} style={{ color: 'var(--brand-primary)' }} />
              <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Loading your documents...</span>
            </div>
          ) : error ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '2rem', background: 'rgba(239, 68, 68, 0.05)', border: '1px solid rgba(239, 68, 68, 0.1)', borderRadius: 'var(--radius-lg)', color: '#f87171' }}>
              <AlertCircle size={20} />
              <span style={{ fontSize: '0.875rem' }}>{error}</span>
            </div>
          ) : filteredDocs.length === 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '5rem 0', textAlign: 'center', gap: '0.75rem' }}>
              <FileText size={40} style={{ color: 'var(--text-muted)', opacity: 0.5 }} />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                {searchQuery ? 'No documents match your search' : 'No documents uploaded yet'}
              </h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', maxWidth: '360px' }}>
                {searchQuery ? 'Try adjusting your query term.' : 'Upload a PDF contract or NDA to start using security and compliance analyses.'}
              </p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)', color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Filename</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Version</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Upload Date</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredDocs.map((doc) => (
                    <tr 
                      key={doc.id}
                      style={{ 
                        borderBottom: '1px solid rgba(255, 255, 255, 0.03)',
                        fontSize: '0.9rem',
                        transition: 'background-color 0.15s ease'
                      }}
                      onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.01)'}
                      onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    >
                      <td style={{ padding: '1rem', fontWeight: 500 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <FileText size={18} style={{ color: 'var(--brand-primary)', flexShrink: 0 }} />
                          <span 
                            onClick={() => onSelectDocument(doc)} 
                            style={{ cursor: 'pointer', color: 'var(--text-primary)', transition: 'color 0.15s' }}
                            onMouseOver={(e) => e.target.style.color = '#fff'}
                            onMouseOut={(e) => e.target.style.color = 'var(--text-primary)'}
                          >
                            {doc.filename}
                          </span>
                        </div>
                      </td>
                      <td style={{ padding: '1rem' }}>
                        <span style={{ 
                          display: 'inline-flex', 
                          alignItems: 'center', 
                          gap: '0.35rem', 
                          padding: '0.2rem 0.6rem', 
                          borderRadius: '4px', 
                          background: 'rgba(99, 102, 241, 0.08)', 
                          color: '#818cf8', 
                          fontSize: '0.75rem',
                          fontWeight: 600
                        }}>
                          <Layers size={11} />
                          v{doc.version_number}
                        </span>
                      </td>
                      <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
                          <Calendar size={13} style={{ color: 'var(--text-muted)' }} />
                          {formatDate(doc.upload_timestamp)}
                        </div>
                      </td>
                      <td style={{ padding: '1rem', textAlign: 'right', position: 'relative' }}>
                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', alignItems: 'center' }}>
                          
                          <button
                            onClick={() => {
                              setVersionTarget(doc);
                              versionFileInputRef.current?.click();
                            }}
                            style={{
                              background: 'transparent',
                              border: '1px solid rgba(255, 255, 255, 0.06)',
                              color: 'var(--text-secondary)',
                              padding: '0.35rem 0.65rem',
                              borderRadius: 'var(--radius-md)',
                              fontSize: '0.75rem',
                              fontWeight: 500,
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.3rem',
                              transition: 'all 0.15s'
                            }}
                            onMouseOver={(e) => {
                              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.15)';
                              e.currentTarget.style.color = 'var(--text-primary)';
                            }}
                            onMouseOut={(e) => {
                              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.06)';
                              e.currentTarget.style.color = 'var(--text-secondary)';
                            }}
                          >
                            <History size={11} />
                            + Version
                          </button>

                          <button
                            onClick={() => onSelectDocument(doc)}
                            style={{
                              background: 'rgba(99, 102, 241, 0.12)',
                              border: '1px solid rgba(99, 102, 241, 0.25)',
                              color: '#a5b4fc',
                              padding: '0.35rem 0.65rem',
                              borderRadius: 'var(--radius-md)',
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.3rem',
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
                            Open
                          </button>

                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteDocument(doc.id);
                            }}
                            style={{
                              background: 'rgba(239, 68, 68, 0.12)',
                              border: '1px solid rgba(239, 68, 68, 0.25)',
                              color: '#f87171',
                              padding: '0.35rem 0.65rem',
                              borderRadius: 'var(--radius-md)',
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              cursor: 'pointer',
                              transition: 'all 0.15s'
                            }}
                            onMouseOver={(e) => {
                              e.currentTarget.style.background = '#ef4444';
                              e.currentTarget.style.color = '#fff';
                              e.currentTarget.style.borderColor = '#ef4444';
                            }}
                            onMouseOut={(e) => {
                              e.currentTarget.style.background = 'rgba(239, 68, 68, 0.12)';
                              e.currentTarget.style.color = '#f87171';
                              e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.25)';
                            }}
                          >
                            Delete
                          </button>

                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MyDocuments;
