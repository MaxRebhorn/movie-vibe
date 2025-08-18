import React from 'react';
import '../../styles/colors.css';

const Text = ({ variant, children, color = 'default', ...props }) => {
  const getColorClass = () => {
    switch(color) {
      case 'accent': return 'text-rgb-217-33-44';
      case 'muted': return 'text-rgb-179-179-179';
      case 'white': return 'text-white';
      default: return 'text-rgb-245-245-245';
    }
  };

  return (
    <p
      className={`text-${variant} ${getColorClass()}`}
      {...props}
    >
      {children}
    </p>
  );
};

export default Text;