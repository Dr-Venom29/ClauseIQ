import React from 'react';
import { cn } from '../../lib/utils';
import './ui.css';

export const Skeleton = ({ className, ...props }) => {
  return <div className={cn('ui-skeleton', className)} {...props} />;
};
