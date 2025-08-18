import React from 'react';
import '../../styles/colors.css';

export const Icon = ({ src, alt = '', style = {}, className = '' }) => {
  const iconStyle = {
    flexGrow: 0,
    flexShrink: 1,
    flexBasis: 'auto',
    ...style
  };

  return <img src={src} alt={alt} style={iconStyle} className={className} />;
};
