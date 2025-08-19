// src/molecules/IconButton.jsx
import React from 'react';
import Icon from '../../atoms/Icon/Icon';
import '../../../styles/colors.css';
import styles from './IconButton.module.css';

const IconButton = ({ name, alt, onClick, className = '' }) => {
  return (
    <button
      onClick={onClick}
      className={`${styles.button} ${className}`}
      aria-label={alt}
    >
      <Icon name={name} alt={alt} />
    </button>
  );
};

export default IconButton;
