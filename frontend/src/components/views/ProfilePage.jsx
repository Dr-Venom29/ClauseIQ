import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { User, Shield, Mail, ShieldCheck } from 'lucide-react';
import './views.css';

const ProfilePage = () => {
  const { currentUser } = useAuth();

  const getDisplayName = () => {
    if (!currentUser?.email) return 'User';
    const parts = currentUser.email.split('@')[0];
    return parts.charAt(0).toUpperCase() + parts.slice(1);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', padding: '1rem 0' }}>
      
      {/* Header */}
      <div style={{ textAlign: 'center' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 700, letterSpacing: '-0.03em' }}>
          User Profile
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.925rem', marginTop: '0.25rem' }}>
          Manage your account profile and verify API authorizations.
        </p>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', width: '100%', marginTop: '1rem' }}>
        
        {/* Profile Card */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(30, 30, 38, 0.4) 0%, rgba(20, 20, 25, 0.25) 100%)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          borderRadius: 'var(--radius-xl)',
          padding: '3rem 2.5rem',
          boxShadow: '0 12px 40px 0 rgba(0, 0, 0, 0.3)',
          display: 'flex',
          flexDirection: 'column',
          gap: '2.5rem',
          width: '100%',
          maxWidth: '640px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
            <div style={{
              width: '90px',
              height: '90px',
              borderRadius: '50%',
              background: 'rgba(99, 102, 241, 0.1)',
              border: '1px solid rgba(99, 102, 241, 0.25)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--brand-primary)',
              flexShrink: 0
            }}>
              <User size={42} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>{getDisplayName()}</h2>
              <span style={{ 
                display: 'inline-flex', 
                alignItems: 'center', 
                gap: '0.35rem', 
                marginTop: '0.6rem', 
                padding: '0.25rem 0.75rem', 
                borderRadius: '6px', 
                background: 'rgba(52, 211, 153, 0.08)', 
                color: '#34d399', 
                fontSize: '0.775rem',
                fontWeight: 600
              }}>
                <ShieldCheck size={13} />
                Verified Account Owner
              </span>
            </div>
          </div>

          <div style={{ height: '1px', background: 'rgba(255, 255, 255, 0.06)' }} />

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.05em' }}>
                <Mail size={14} />
                Registered Email
              </div>
              <div style={{ fontSize: '1.05rem', fontWeight: 500, color: 'var(--text-primary)', marginTop: '0.45rem' }}>
                {currentUser?.email || 'N/A'}
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.05em' }}>
                <Shield size={14} />
                Tenant Identifier (user_id)
              </div>
              <div style={{ 
                fontSize: '0.875rem', 
                fontFamily: 'monospace', 
                background: 'rgba(0, 0, 0, 0.25)', 
                border: '1px solid rgba(255, 255, 255, 0.05)', 
                borderRadius: 'var(--radius-md)', 
                padding: '0.75rem 1rem', 
                color: 'var(--text-secondary)',
                marginTop: '0.45rem',
                wordBreak: 'break-all'
              }}>
                {currentUser?.id || 'N/A'}
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};

export default ProfilePage;
