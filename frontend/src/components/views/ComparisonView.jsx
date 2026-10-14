import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Button } from '../ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Skeleton } from '../ui/Skeleton';
import { ArrowRightLeft, UploadCloud, AlertCircle, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

const ComparisonView = ({ documentId, onCompareComplete }) => {
  const [comparisonDocId, setComparisonDocId] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [comparing, setComparing] = useState(false);
  const [results, setResults] = useState(null);
  const fileInputRef = useRef(null);

  const handleUploadVersion = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`http://localhost:8000/api/v1/documents/${documentId}/version`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const newDocId = response.data.id;
      setComparisonDocId(newDocId);
      runComparison(newDocId);
    } catch (err) {
      alert('Failed to upload comparison version.');
      setUploading(false);
    }
  };

  const runComparison = async (docBId) => {
    setComparing(true);
    setUploading(false);
    try {
      const response = await axios.post('http://localhost:8000/api/v1/compare', {
        doc_a_id: documentId,
        doc_b_id: docBId
      });
      setResults(response.data);
      if (onCompareComplete) onCompareComplete(response.data);
    } catch (err) {
      alert("Failed to run comparison.");
    } finally {
      setComparing(false);
    }
  };

  if (!results && !comparing) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
        <div style={{ background: 'var(--bg-tertiary)', width: '80px', height: '80px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem auto' }}>
          <ArrowRightLeft size={40} color="var(--brand-primary)" />
        </div>
        <h2 style={{ marginBottom: '1rem' }}>Compare Document Versions</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', maxWidth: '500px', margin: '0 auto 2rem auto' }}>
          Upload a revised version of this contract. ClauseIQ will run a semantic diff to highlight added, removed, and modified clauses, along with AI impact analysis.
        </p>
        <input type="file" accept="application/pdf" style={{ display: 'none' }} ref={fileInputRef} onChange={handleUploadVersion} />
        <Button variant="primary" size="lg" onClick={() => fileInputRef.current?.click()} disabled={uploading}>
          {uploading ? 'Uploading...' : 'Upload Revision to Compare'}
        </Button>
      </div>
    );
  }

  if (comparing) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Loader2 className="spin" size={24} /> Analyzing Differentials...
        </h3>
        <Skeleton style={{ height: '120px' }} />
        <Skeleton style={{ height: '120px' }} />
        <style>{`@keyframes spin { 100% { transform: rotate(360deg); } } .spin { animation: spin 2s linear infinite; }`}</style>
      </div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      
      <div style={{ display: 'flex', gap: '1rem' }}>
        <Card style={{ flex: 1, borderTop: '4px solid var(--status-success)' }}>
          <CardHeader><CardTitle>Added</CardTitle></CardHeader>
          <CardContent><div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--status-success)' }}>{results.added?.length || 0}</div></CardContent>
        </Card>
        <Card style={{ flex: 1, borderTop: '4px solid var(--status-danger)' }}>
          <CardHeader><CardTitle>Removed</CardTitle></CardHeader>
          <CardContent><div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--status-danger)' }}>{results.removed?.length || 0}</div></CardContent>
        </Card>
        <Card style={{ flex: 1, borderTop: '4px solid var(--status-warning)' }}>
          <CardHeader><CardTitle>Modified</CardTitle></CardHeader>
          <CardContent><div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--status-warning)' }}>{results.modified?.length || 0}</div></CardContent>
        </Card>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {results.modified?.map((mod, i) => (
          <Card key={`m-${i}`} style={{ borderLeft: '4px solid var(--status-warning)' }}>
            <CardHeader style={{ paddingBottom: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <CardTitle style={{ fontSize: '1.125rem' }}>Modified Clause</CardTitle>
                <Badge variant="warning">Impact: {mod.impact_analysis}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div style={{ padding: '1rem', background: 'var(--status-danger-bg)', borderRadius: 'var(--radius-md)', color: 'var(--text-secondary)' }}>
                   <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--status-danger)', marginBottom: '0.5rem' }}>ORIGINAL</div>
                   <del>{mod.original}</del>
                </div>
                <div style={{ padding: '1rem', background: 'var(--status-success-bg)', borderRadius: 'var(--radius-md)', color: 'var(--text-secondary)' }}>
                   <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--status-success)', marginBottom: '0.5rem' }}>REVISION</div>
                   <ins style={{ textDecoration: 'none' }}>{mod.new}</ins>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {results.added?.map((add, i) => (
          <Card key={`a-${i}`} style={{ borderLeft: '4px solid var(--status-success)' }}>
            <CardHeader style={{ paddingBottom: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <CardTitle style={{ fontSize: '1.125rem' }}>Added Clause</CardTitle>
                <Badge variant="success">New</Badge>
              </div>
            </CardHeader>
            <CardContent>
               <div style={{ padding: '1rem', background: 'var(--status-success-bg)', borderRadius: 'var(--radius-md)', color: 'var(--text-secondary)' }}>
                 {add}
               </div>
            </CardContent>
          </Card>
        ))}

        {results.removed?.map((rem, i) => (
          <Card key={`r-${i}`} style={{ borderLeft: '4px solid var(--status-danger)' }}>
            <CardHeader style={{ paddingBottom: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <CardTitle style={{ fontSize: '1.125rem' }}>Removed Clause</CardTitle>
                <Badge variant="danger">Deleted</Badge>
              </div>
            </CardHeader>
            <CardContent>
               <div style={{ padding: '1rem', background: 'var(--status-danger-bg)', borderRadius: 'var(--radius-md)', color: 'var(--text-secondary)' }}>
                 <del>{rem}</del>
               </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </motion.div>
  );
};

export default ComparisonView;
