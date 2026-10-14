import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import Login from '../pages/Login';
import Register from '../pages/Register';

const AuthGate = () => {
  const [view, setView] = useState('login');
  return view === 'login' ? (
    <Login onToggle={() => setView('register')} />
  ) : (
    <Register onToggle={() => setView('login')} />
  );
};

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh', 
        backgroundColor: '#0e0e11', 
        color: '#e4e4e7',
        fontFamily: 'var(--font-sans)'
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
          <svg width="40" height="40" viewBox="0 0 80 80" fill="none">
            <circle cx="40" cy="40" r="36" stroke="rgba(99,102,241,0.15)" strokeWidth="3"/>
            <circle cx="40" cy="40" r="36" stroke="#6366f1" strokeWidth="3"
              strokeDasharray="56 170" strokeLinecap="round">
              <animateTransform attributeName="transform" type="rotate"
                from="0 40 40" to="360 40 40" dur="1s" repeatCount="indefinite"/>
            </circle>
          </svg>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Loading session...</div>
        </div>
      </div>
    );
  }

  return isAuthenticated ? children : <AuthGate />;
};

export default ProtectedRoute;

