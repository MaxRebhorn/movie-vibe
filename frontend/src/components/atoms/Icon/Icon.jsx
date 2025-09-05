import React from 'react';
import styles from './Icon.module.css';

const Icon = ({ name, alt = '', className = '', ...props }) => {
  return (
    <img
      src={`/${name}`}
      alt={alt}
      className={`${styles.icon} ${className}`}
      {...props}
    />
  );
};

export default Icon;
