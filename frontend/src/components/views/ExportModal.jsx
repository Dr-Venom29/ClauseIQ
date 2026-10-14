import React, { useState } from 'react';
import axios from 'axios';
import { Button } from '../ui/Button';
import { Download, FileJson, FileText, FileBadge } from 'lucide-react';
import { motion } from 'framer-motion';
import './views.css';

const ExportModal = ({ documentId }) => {
  const [downloading, setDownloading] = useState(false);

  const handleExport = async (format) => {
    setDownloading(format);
    try {
      const response = await axios.post(`http://localhost:8000/api/v1/documents/${documentId}/export?export_format=${format}`);
      const { download_url } = response.data;
      
      // trigger download
      window.open(`http://localhost:8000${download_url}`, '_blank');
    } catch (err) {
      alert("Export failed.");
    } finally {
      setDownloading(false);
    }
  };

  const formats = [
    { id: 'pdf', name: 'PDF Report', icon: FileBadge, desc: 'Professional, uneditable report for external sharing.' },
    { id: 'docx', name: 'Word Document', icon: FileText, desc: 'Fully editable report for internal review and redlining.' },
    { id: 'json', name: 'Raw JSON', icon: FileJson, desc: 'Machine-readable format for API integrations and data lakes.' }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }} 
      animate={{ opacity: 1, y: 0 }} 
      style={{ maxWidth: '900px', margin: '0 auto', padding: '1rem 0' }}
    >
      {/* Centered Premium Header */}
      <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 700, letterSpacing: '-0.03em', marginBottom: '1rem', color: 'var(--text-primary)' }}>
          Export Intelligence Center
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', maxWidth: '600px', margin: '0 auto', lineHeight: '1.6' }}>
          Generate comprehensive audit reports containing the executive summary, compliance checklist, and risk analysis.
        </p>
      </div>

      {/* Grid Layout Cards */}
      <div className="export-center-grid">
        {formats.map(f => (
          <div key={f.id} className="export-card">
            <div className="export-icon-box">
              <f.icon size={28} />
            </div>
            
            <div className="export-details">
              <h3 className="export-title">{f.name}</h3>
              <p className="export-desc">{f.desc}</p>
            </div>
            
            <Button 
              variant="primary" 
              onClick={() => handleExport(f.id)}
              disabled={downloading !== false}
              style={{ display: 'flex', gap: '0.5rem', width: '100%', justifyContent: 'center' }}
            >
              {downloading === f.id ? (
                'Generating...'
              ) : (
                <>
                  <Download size={16} />
                  <span>Export</span>
                </>
              )}
            </Button>
          </div>
        ))}
      </div>
    </motion.div>
  );
};

export default ExportModal;
