import React from 'react';
import { Link } from 'react-router-dom';
import Text from '../../atoms/Text/Text';
import Tag from '../../atoms/Tag/Tag';
import '../../../styles/colors.css';
import styles from './ProductCard.module.css';

const ProductCard = ({
  id,               // <-- now you receive id properly
  className = '',
  style = {},
  image,
  title,
  director,
  cast = [],
  keywords = [],
  releaseYear
}) => {
  const topCast = cast.slice(0, 3);
  const topTags = keywords.slice(0, 4);

  return (
      <div className={`${styles.card} ${className}`} style={style}>
           <Link to={`/movies/${id}`} className={styles.linkWrapper}>
        <img src={image} alt={title} className={styles.image} />
           </Link>
        <div className={styles.content}>
          <div className={styles.textContent}>
            <Text variant="strong">{title}</Text>
            {director && <Text variant="small-bold">{director}</Text>}
            {topCast.length > 0 && (
              <div className={styles.cast}>
                {topCast.map((member, idx) => (
                  <Text key={idx} variant="extra-small" color="muted">
                    {member}
                  </Text>
                ))}
              </div>
            )}
          </div>
          {releaseYear && (
            <div className={styles.year}>
              <Text variant="small">{releaseYear}</Text>
            </div>
          )}
        </div>
        {topTags.length > 0 && (
          <div className={styles.tags}>
            {topTags.map((tag, idx) => (
              <Tag key={idx} label={tag} color="accent" size="small" />
            ))}
          </div>
        )}
      </div>
  );
};

export default ProductCard;
