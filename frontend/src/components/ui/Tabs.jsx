import React, { createContext, useContext, useState } from 'react';
import { cn } from '../../lib/utils';
import './ui.css';

const TabsContext = createContext(null);

export const Tabs = ({ defaultValue, onValueChange, className, children, ...props }) => {
  const [activeTab, setActiveTab] = useState(defaultValue);

  const handleTabChange = (value) => {
    setActiveTab(value);
    if (onValueChange) onValueChange(value);
  };

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab: handleTabChange }}>
      <div className={cn('ui-tabs', className)} {...props}>
        {children}
      </div>
    </TabsContext.Provider>
  );
};

export const TabsList = ({ className, children, ...props }) => {
  return (
    <div className={cn('ui-tabs-list', className)} {...props}>
      {children}
    </div>
  );
};

export const TabsTrigger = ({ value, className, children, ...props }) => {
  const { activeTab, setActiveTab } = useContext(TabsContext);
  const isActive = activeTab === value;

  return (
    <button
      className={cn('ui-tabs-trigger', isActive && 'active', className)}
      onClick={() => setActiveTab(value)}
      {...props}
    >
      {children}
    </button>
  );
};

export const TabsContent = ({ value, className, children, ...props }) => {
  const { activeTab } = useContext(TabsContext);
  if (activeTab !== value) return null;
  return (
    <div className={cn('ui-tabs-content', className)} {...props}>
      {children}
    </div>
  );
};
