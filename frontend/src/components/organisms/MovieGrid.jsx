import React from 'react';
import ProductCard from '../molecules/ProductCard';
import '../../styles/colors.css';

const MovieGrid = ({ movies }) => {
  if (!movies || movies.length === 0) {
    return <div className="movie-grid">No movies found</div>;
  }

  return (
    <div className="movie-grid">
      {movies.map(movie => (
        <ProductCard
          key={movie.id}
          image={movie.poster_url || '/images/default.png'}
          title={movie.title}
          director={movie.director || "Unknown"}
          tags={movie.tags || ""}
        />
      ))}
    </div>
  );
};

export default MovieGrid;
