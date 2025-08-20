// Button.jsx (Fixed)
import React from 'react';
import Text from '../Text/Text';
import '../../../styles/colors.css';
import styles from './Button.module.css';

const Button = ({ children, variant = 'default', ...props }) => {
  return (
    <button className={`${styles.button} ${styles[variant]}`} {...props}>
      <Text variant="button">{children}</Text>
    </button>
  );
};

export default Button;