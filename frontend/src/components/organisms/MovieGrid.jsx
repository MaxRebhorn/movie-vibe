import React from 'react';
import ProductCard from '../molecules/ProductCard';
import '../../styles/colors.css';

const MovieGrid = () => {
  const movies = [
    { id: 1, image: '/images/image-19.png', title: 'Title', director: 'Director', tags: 'Tag List' },
    { id: 2, image: '/images/image-28.png', title: 'Title', director: 'Director', tags: 'Tag List' },
    { id: 3, image: '/images/image-37.png', title: 'Title', director: 'Director', tags: 'Tag List' },
  ];

  return (
    <div className="movie-grid">
      {movies.map(movie => (
        <ProductCard key={movie.id} {...movie} />
      ))}
    </div>
  );
};

export default MovieGrid;