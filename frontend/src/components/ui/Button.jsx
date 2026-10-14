import React from 'react';
import { cn } from '../../lib/utils';
import './ui.css';

export const Button = React.forwardRef(({ className, variant = 'primary', size = 'default', ...props }, ref) => {
  return (
    <button
      ref={ref}
      className={cn('ui-button', variant, size, className)}
      {...props}
    />
  );
});
Button.displayName = 'Button';
