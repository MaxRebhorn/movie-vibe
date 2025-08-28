import React from 'react';
import Text from '../Text/Text';
import '../../../styles/colors.css';
import styles from './Button.module.css';
import anim from '../../../styles/animation.module.css';

const Button = ({ children, variant = 'default', className = '', ...props }) => {
  return (
    <button
      className={`
        ${styles.button}
        ${styles[variant]}
        ${anim.btnPress}
        ${anim.hoverLift}
        ${className}
      `}
      {...props}
    >
      <Text variant="button">{children}</Text>
    </button>
  );
};

export default Button;
