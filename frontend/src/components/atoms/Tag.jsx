// src/components/atoms/Tag.jsx
import React from 'react';
import Text from './Text';
import '../../styles/colors.css'; // for color classes

const Tag = ({ label, color = 'primary', size = 'default' }) => {
  const sizeStyles = {
    small: {
      padding: '1px 6px',
      borderRadius: '8px',
      fontSize: '10px'
    },
    default: {
      padding: '2px 8px',
      borderRadius: '12px'
    }
  };

  return (
    <div
      className={`tag tag-${color}`}
      style={{
        display: 'inline-block',
        ...sizeStyles[size],
        backgroundColor: 'var(--' + color + ')',
        marginRight: '4px',
        marginBottom: '4px',
      }}
    >
      <Text variant="extra-small" color="onPrimary">{label}</Text>
    </div>
  );
};

export default Tag;
