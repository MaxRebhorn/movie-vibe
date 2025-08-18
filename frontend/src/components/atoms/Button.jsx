import React from 'react';
import Text from './Text';
import '../../styles/colors.css';

const Button = ({ children, ...props }) => {
  return (
    <button className="button" {...props}>
      <Text variant="button">{children}</Text>
    </button>
  );
};

export default Button;