import React from 'react';
import styles from './Button.module.css';
import anim from '../../../styles/animation.module.css';

const Button = ({
  children,
  variant = 'default',
  onClick,
  disabled = false,
  type = 'button',
  className = ''
}) => {
  return (
    <button
      type={type}
      className={`${styles.button} ${styles[variant]} ${anim.btnPress} ${anim.hoverLift} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

export default Button;