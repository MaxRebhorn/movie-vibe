import React from 'react';
import ProductCard from '../molecules/ProductCard';
import '../../styles/colors.css';

const MovieGrid = ({movies}) => {
    if (!movies || movies.length === 0) {
        return <div className="movie-grid">No movies found</div>;
    }

    return (
        <div className="movie-grid">
            {movies.map(movie => (
                <ProductCard
                    key={movie.id}
                    image={movie.poster_url}
                    title={movie.title}
                    director={movie.director}
                    cast={movie.cast}
                    keywords={movie.keywords} // Changed from tags
                    releaseYear={movie.release_date?.split('-')[0]}
                />
            ))}
        </div>
    );
};

export default MovieGrid;
