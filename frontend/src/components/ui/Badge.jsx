import React from 'react';
import { cn } from '../../lib/utils';
import './ui.css';

export const Badge = React.forwardRef(({ className, variant = 'default', ...props }, ref) => {
  return (
    <div ref={ref} className={cn('ui-badge', variant, className)} {...props} />
  );
});
Badge.displayName = 'Badge';
