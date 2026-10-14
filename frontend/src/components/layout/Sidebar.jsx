import React from 'react';
import { FileText, LayoutDashboard, SplitSquareHorizontal, Download, Activity, Settings, ChevronLeft, ChevronRight, Scale, LogOut, User as UserIcon, UploadCloud } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useAuth } from '../../context/AuthContext';
import logoImg from '../../assets/logo.png';
import './layout.css';

const Sidebar = ({ isCollapsed, setIsCollapsed, activeRoute, setActiveRoute }) => {
  const { currentUser, logout } = useAuth();
  
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'documents', label: 'My Documents', icon: FileText },
    { id: 'upload', label: 'Upload', icon: UploadCloud },
    { id: 'compare', label: 'Compare', icon: SplitSquareHorizontal },
    { id: 'analytics', label: 'Analytics', icon: Activity },
    { id: 'profile', label: 'Profile', icon: UserIcon },
  ];

  return (
    <div className="layout-sidebar" style={{ width: isCollapsed ? '72px' : '280px' }}>
      {!isCollapsed ? (
        <div className="sidebar-logo" style={{ 
          padding: '1.5rem 1.5rem', 
          justifyContent: 'flex-start',
          overflow: 'hidden',
          width: '100%'
        }}>
          <img 
            src={logoImg} 
            alt="ClauseIQ Logo" 
            style={{ 
              height: '65px', 
              width: 'auto', 
              objectFit: 'contain',
              display: 'block'
            }} 
          />
        </div>
      ) : (
        <div style={{ height: '84px' }} />
      )}

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <div
            key={item.id}
            className={cn('sidebar-item', activeRoute === item.id && 'active')}
            onClick={() => setActiveRoute(item.id)}
            title={isCollapsed ? item.label : undefined}
          >
            <item.icon size={20} />
            {!isCollapsed && <span>{item.label}</span>}
          </div>
        ))}
      </nav>

      {currentUser && (
        <div style={{
          padding: '1.25rem 1rem',
          borderTop: '1px solid rgba(255, 255, 255, 0.04)',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
          marginTop: 'auto',
          overflow: 'hidden'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            color: 'var(--text-secondary)',
            fontSize: '0.825rem'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              color: 'var(--text-secondary)',
              flexShrink: 0
            }}>
              <UserIcon size={13} />
            </div>
            {!isCollapsed && (
              <span style={{ 
                overflow: 'hidden', 
                textOverflow: 'ellipsis', 
                whiteSpace: 'nowrap',
                fontWeight: 500
              }}>
                {currentUser.email}
              </span>
            )}
          </div>
          
          <button
            onClick={logout}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: isCollapsed ? 'center' : 'flex-start',
              gap: '0.75rem',
              width: '100%',
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              color: 'var(--text-secondary)',
              padding: '0.55rem 0.75rem',
              borderRadius: 'var(--radius-md)',
              cursor: 'pointer',
              fontSize: '0.825rem',
              fontWeight: 500,
              transition: 'background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease',
              outline: 'none'
            }}
            onMouseOver={e => {
              e.currentTarget.style.background = 'rgba(239, 68, 68, 0.06)';
              e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.15)';
              e.currentTarget.style.color = '#f87171';
            }}
            onMouseOut={e => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)';
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.05)';
              e.currentTarget.style.color = 'var(--text-secondary)';
            }}
            title={isCollapsed ? 'Log Out' : undefined}
          >
            <LogOut size={15} style={{ flexShrink: 0 }} />
            {!isCollapsed && <span>Log Out</span>}
          </button>
        </div>
      )}

      <div className="sidebar-toggle">
        <button onClick={() => setIsCollapsed(!isCollapsed)}>
          {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;

