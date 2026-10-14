import React, { useState, useRef } from 'react';
import axios from 'axios';
import Chat from './Chat';
import SummaryView from './SummaryView';
import ChecklistView from './ChecklistView';
import RiskAnalysisView from './RiskAnalysisView';
import ExportReport from './ExportReport';
import ComparisonDashboard from './ComparisonDashboard';

const Dashboard = ({ documentId }) => {
  const [activeTab, setActiveTab] = useState('chat');
  const [comparisonDocId, setComparisonDocId] = useState(null);
  const [uploadingVersion, setUploadingVersion] = useState(false);
  const fileInputRef = useRef(null);

  const tabStyle = (tabName) => ({
    padding: '10px 20px',
    cursor: 'pointer',
    backgroundColor: activeTab === tabName ? '#646cff' : '#f0f0f0',
    color: activeTab === tabName ? 'white' : 'black',
    border: 'none',
    marginRight: '10px',
    borderRadius: '5px'
  });

  const handleUploadVersion = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadingVersion(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`http://localhost:8000/api/v1/documents/${documentId}/version`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setComparisonDocId(response.data.id);
      setActiveTab('comparison');
    } catch (err) {
      alert('Failed to upload new version.');
    } finally {
      setUploadingVersion(false);
    }
  };

  if (activeTab === 'comparison' && comparisonDocId) {
    return <ComparisonDashboard docAId={documentId} docBId={comparisonDocId} onBack={() => setActiveTab('chat')} />;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px', alignItems: 'center' }}>
        <div>
          <button style={tabStyle('chat')} onClick={() => setActiveTab('chat')}>Chat</button>
          <button style={tabStyle('summary')} onClick={() => setActiveTab('summary')}>Summary</button>
          <button style={tabStyle('checklist')} onClick={() => setActiveTab('checklist')}>Checklist</button>
          <button style={tabStyle('risks')} onClick={() => setActiveTab('risks')}>Risks</button>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input type="file" accept="application/pdf" style={{ display: 'none' }} ref={fileInputRef} onChange={handleUploadVersion} />
          <button 
            onClick={() => fileInputRef.current.click()} 
            disabled={uploadingVersion}
            style={{ padding: '10px 20px', backgroundColor: '#1976d2', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
            {uploadingVersion ? 'Uploading...' : 'Compare New Version'}
          </button>
          <ExportReport documentId={documentId} />
        </div>
      </div>

      <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '8px', minHeight: '400px' }}>
        {activeTab === 'chat' && <Chat documentId={documentId} />}
        {activeTab === 'summary' && <SummaryView documentId={documentId} />}
        {activeTab === 'checklist' && <ChecklistView documentId={documentId} />}
        {activeTab === 'risks' && <RiskAnalysisView documentId={documentId} />}
      </div>
    </div>
  );
};

export default Dashboard;
