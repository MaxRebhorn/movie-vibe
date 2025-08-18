import React from 'react';
import Text from '../atoms/Text';
import '../../styles/colors.css';

const ProductCard = ({ image, title, director, tags }) => {
  return (
    <div className="product-card">
      <img src={image} alt={title} className="product-image" />
      <div className="card-body">
        <Text variant="body">{title}</Text>
        <Text variant="strong">{director}</Text>
        <Text variant="small" color="muted">{tags}</Text>
      </div>
    </div>
  );
};

export default ProductCard;