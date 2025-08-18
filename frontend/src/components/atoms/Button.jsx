// Button.jsx
import React from 'react';
import { Text } from './Text';
import '../../styles/colors.css';

export const Button = ({ children, style = {}, className = '' }) => {
  const buttonStyle = {
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '8px',
    padding: '14px 24px',
    flexGrow: 0,
    flexShrink: 1,
    flexBasis: 'auto',
    boxShadow: '0px 1px 2px rgba(0,0,0,0.5)',
    borderRadius: '8px',
    backgroundColor: 'rgba(20, 20, 23, 1)', // layout background stays in JSX
    ...style
  };

  return (
    <div style={buttonStyle} className={className}>
      <Text variant="button">{children}</Text>
    </div>
  );
};
