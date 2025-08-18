// Text.jsx
import React from 'react';
import '../../styles/colors.css';

export const Text = ({
  variant = 'body',
  color = 'white',
  children,
  className = '',
  style = {}
}) => {
  const baseStyle = {
    fontFamily: variant === 'heading' ? 'Roboto, sans-serif' : 'Inter, sans-serif',
    ...(variant === 'heading' && {
      fontSize: '57px',
      lineHeight: '64px',
      letterSpacing: '-0.25px',
      fontWeight: 'normal'
    }),
    ...(variant === 'body' && {
      fontSize: '16px',
      lineHeight: '1.5',
      fontWeight: 'normal'
    }),
    color: `var(--text-${color})`, // colors still come from CSS
    ...style
  };

  return (
    <p style={baseStyle} className={className}>
      {children}
    </p>
  );
};
