import React, { useState } from 'react';
import Sidebar from './Sidebar';
import './layout.css';

const DashboardLayout = ({ 
  children, 
  activeRoute, 
  setActiveRoute
}) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  return (
    <div className="layout-container">
      <Sidebar 
        isCollapsed={isSidebarCollapsed} 
        setIsCollapsed={setIsSidebarCollapsed} 
        activeRoute={activeRoute}
        setActiveRoute={setActiveRoute}
      />
      
      <main className="layout-main">
        <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
          {children}
        </div>
      </main>
    </div>
  );
};

export default DashboardLayout;
