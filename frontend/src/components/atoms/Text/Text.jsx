import React from 'react';
import '../../../styles/global.css';
import '../../../styles/colors.css';
const Text = ({ variant, children, color = 'default', ...props }) => {
  const colorClass = color === 'accent' ? 'text-accent' :
                   color === 'muted' ? 'text-muted' :
                   color === 'white' ? 'text-white' : '';

  return (
    <p
      className={`text-${variant} ${colorClass}`}
      {...props}
    >
      {children}
    </p>
  );
};

export default Text;