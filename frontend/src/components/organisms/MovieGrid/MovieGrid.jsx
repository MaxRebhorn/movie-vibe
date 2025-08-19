import React, { useEffect, useState } from 'react';
import ProductCard from '../../molecules/ProductCard/ProductCard';
import styles from './MovieGrid.module.css';

const MovieGrid = ({ movies }) => {
  const [animatedMovies, setAnimatedMovies] = useState([]);

  useEffect(() => {
    if (movies.length) {
      // small delay before starting animation
      const timer = setTimeout(() => setAnimatedMovies(movies), 50);
      return () => clearTimeout(timer);
    } else {
      setAnimatedMovies([]);
    }
  }, [movies]);

  if (!movies || movies.length === 0) {
    return <div className={styles.grid}>No movies found</div>;
  }

  return (
    <div className={styles.grid}>
      {animatedMovies.map((movie, index) => (
        <ProductCard
          key={movie.id}
          className={styles.animatedCard}
          style={{ animationDelay: `${index * 0.05}s` }}
          image={movie.poster_url}
          title={movie.title}
          director={movie.director}
          cast={movie.cast}
          keywords={movie.keywords}
          releaseYear={movie.release_date?.split('-')[0]}
        />
      ))}
    </div>
  );
};

export default MovieGrid;
