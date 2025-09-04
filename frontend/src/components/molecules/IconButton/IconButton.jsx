import React from 'react';
import Icon from '../../atoms/Icon/Icon';
import '../../../styles/colors.css';
import styles from './IconButton.module.css';

/**
 * IconButton - atomized button
 * Props:
 * - name: icon filename
 * - alt: alt text
 * - onClick: click handler
 * - className: extra CSS classes
 * - iconStyle: optional inline style for the icon (like fill, opacity, etc.)
 */
const IconButton = ({ name, alt, onClick, className = '', iconStyle = {} }) => {
  return (
    <button
      onClick={onClick}
      className={`${styles.button} ${className}`}
      aria-label={alt}
    >
      <Icon name={name} alt={alt} style={iconStyle} />
    </button>
  );
};

export default IconButton;
