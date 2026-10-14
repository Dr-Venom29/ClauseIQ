import React, { useState } from 'react';
import DashboardLayout from './components/layout/DashboardLayout';
import LandingPage from './components/views/LandingPage';
import ComparisonView from './components/views/ComparisonView';
import MyDocuments from './components/views/MyDocuments';
import WorkspaceDashboard from './components/views/WorkspaceDashboard';
import AnalyticsPage from './components/views/AnalyticsPage';
import ProfilePage from './components/views/ProfilePage';
import UploadScreen from './components/views/UploadScreen';
import DocumentDetails from './components/views/DocumentDetails';
import { AnimatePresence, motion } from 'framer-motion';
import { AuthProvider, useAuth } from './context/AuthContext';
import { FileText, ArrowRight } from 'lucide-react';

function AppContent() {
  const { isAuthenticated } = useAuth();
  const [document, setDocument] = useState(null);
  const [activeRoute, setActiveRoute] = useState('dashboard');
  const [hasEnteredApp, setHasEnteredApp] = useState(false);

  React.useEffect(() => {
    if (isAuthenticated) {
      setHasEnteredApp(true);
    } else {
      setHasEnteredApp(false);
      setDocument(null);
      setActiveRoute('dashboard');
    }
  }, [isAuthenticated]);

  const handleSelectDocument = (doc) => {
    setDocument(doc);
    if (doc) {
      setActiveRoute('document-details');
    } else {
      setActiveRoute('documents');
    }
  };

  const renderContent = () => {
    if (activeRoute === 'dashboard') {
      return (
        <WorkspaceDashboard 
          setActiveRoute={setActiveRoute} 
          onSelectDocument={handleSelectDocument} 
        />
      );
    }
    if (activeRoute === 'documents') {
      return <MyDocuments onSelectDocument={handleSelectDocument} />;
    }
    if (activeRoute === 'upload') {
      return <UploadScreen onUploadSuccess={handleSelectDocument} />;
    }
    if (activeRoute === 'analytics') {
      return <AnalyticsPage />;
    }
    if (activeRoute === 'profile') {
      return <ProfilePage />;
    }

    // Guard document-dependent views (compare, document-details)
    if (!document) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '60vh',
          textAlign: 'center',
          gap: '1.5rem',
          background: 'linear-gradient(135deg, rgba(30, 30, 38, 0.4) 0%, rgba(20, 20, 25, 0.25) 100%)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          borderRadius: 'var(--radius-xl)',
          padding: '2rem'
        }}>
          <FileText size={48} style={{ color: 'var(--brand-primary)', opacity: 0.8 }} />
          <div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 600 }}>No Active Document Selected</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.5rem', maxWidth: '400px' }}>
              Please select an existing document from your repository or upload a new one to begin.
            </p>
          </div>
          <button 
            onClick={() => setActiveRoute('documents')} 
            style={{
              background: 'var(--brand-primary)',
              border: 'none',
              color: '#fff',
              padding: '0.6rem 1.2rem',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontSize: '0.875rem'
            }}
          >
            Go to Documents
            <ArrowRight size={16} />
          </button>
        </div>
      );
    }

    if (activeRoute === 'compare') {
      return <ComparisonView documentId={document.id} />;
    }

    if (activeRoute === 'document-details') {
      return (
        <DocumentDetails 
          document={document} 
          onSelectDocument={handleSelectDocument} 
          setActiveRoute={setActiveRoute}
        />
      );
    }

    return <div>Route not found</div>;
  };

  return (
    <AnimatePresence mode="wait">
      {!hasEnteredApp ? (
        <motion.div key="landing" style={{ width: '100%', minHeight: '100vh' }} exit={{ opacity: 0, y: -50, scale: 0.98 }} transition={{ duration: 0.5, ease: 'easeInOut' }}>
          <LandingPage onEnterApp={handleSelectDocument} />
        </motion.div>
      ) : (
        <motion.div key="dashboard" style={{ width: '100%', height: '100vh' }} initial={{ opacity: 0, scale: 1.02 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5, ease: 'easeOut' }}>
          <DashboardLayout 
            activeRoute={activeRoute} 
            setActiveRoute={setActiveRoute}
          >
            {renderContent()}
          </DashboardLayout>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
