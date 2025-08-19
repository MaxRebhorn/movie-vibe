// src/molecules/IconButton.jsx
import React from 'react';
import Icon from '../atoms/Icon';
import '../../styles/colors.css';

const IconButton = ({ name, alt, onClick, className = '' }) => {
  return (
    <button
      onClick={onClick}
      className={`icon-button ${className}`}
      aria-label={alt}
    >
      <Icon name={name} alt={alt} />
    </button>
  );
};

export default IconButton;
