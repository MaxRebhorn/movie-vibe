import React from 'react';

const Icon = ({ name, alt, ...props }) => {
   return <img key={name} src={`/${name}`} alt={alt} {...props} />;
};

export default Icon;