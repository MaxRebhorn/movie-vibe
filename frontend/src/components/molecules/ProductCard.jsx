import React from 'react';
import Text from '../atoms/Text';
import Tag from '../atoms/Tag';
import '../../styles/colors.css';

const ProductCard = ({ image, title, director, cast = [], keywords = [], releaseYear }) => {
  const topCast = cast.slice(0, 3);
  const topTags = keywords.slice(0, 4);

  return (
    <div className="product-card">
      <img src={image} alt={title} className="product-image" />
      <div className="card-content">
        <div className="text-content">
          <Text variant="strong">{title}</Text>
          {director && <Text variant="small-bold">{director}</Text>}
          {topCast.length > 0 && (
            <div className="cast-container">
              {topCast.map((member, idx) => (
                <Text key={idx} variant="extra-small" color="muted">
                  {member}
                </Text>
              ))}
            </div>
          )}
        </div>
        {releaseYear && (
          <div className="release-year">
            <Text variant="small">{releaseYear}</Text>
          </div>
        )}
      </div>
      {topTags.length > 0 && (
        <div className="tags-container">
          {topTags.map((tag, idx) => (
            <Tag key={idx} label={tag} color="accent" size="small" />
          ))}
        </div>
      )}
    </div>
  );
};

export default ProductCard;