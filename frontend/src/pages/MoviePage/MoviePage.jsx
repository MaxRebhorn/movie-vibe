import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Navbar from '../../components/organisms/Navbar/Navbar';
import MovieProfile from '../../components/organisms/MovieProfile/MovieProfile';
import MovieGrid from "../../components/organisms/MovieGrid/MovieGrid";
import { movieAPI } from '../../services/api'; // Import the service
import styles from './MoviePage.module.css';
import IconButton from "../../components/molecules/IconButton/IconButton";
import Icon from "../../components/atoms/Icon/Icon";
import anim from "../../styles/animation.module.css";

function MoviePage() {
    const { id } = useParams();
    const [movie, setMovie] = useState(null);
    const [similarMovies, setSimilarMovies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [similarError, setSimilarError] = useState(false);

    // TEMP: replace with your ThemeContext or prop later
    const theme = 'light';

    useEffect(() => {
        async function fetchMovieAndSimilar() {
            setLoading(true);
            try {
                // Fetch main movie
                const movieData = await movieAPI.getMovie(id);
                setMovie(movieData);

                // Fetch similar movies
                try {
                    const similarData = await movieAPI.getSimilarMovies(id);
                    setSimilarMovies(similarData);
                } catch {
                    // Fail gracefully for similar movies
                    setSimilarError(true);
                    setSimilarMovies([]);
                }

            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        }

        if (id) {
            fetchMovieAndSimilar();
        }
    }, [id]);

    if (loading) return <p>Loading...</p>;
    if (error) return <p style={{ color: "red" }}>{error}</p>;
    if (!movie) return <p>No movie found.</p>;

    return (
        <div className={styles.container}>
            <Navbar />
            <main className={styles.main}>
                <MovieProfile
                    title={movie.title}
                    synopsis={movie.synopsis}
                    director={movie.director}
                    releaseDate={movie.release_date}
                    cast={movie.cast}
                    poster={movie.poster_url}
                    trailer={movie.trailer_url}
                    streaming_providers={movie.streaming_providers}
                />

                <Link to={`/movies/${id}/review`} className={`
                    ${styles.linkWrapper}
                    ${anim.btnPress}
                    ${anim.hoverGlow}
                    ${anim.hoverZoom}
                `}>
                    <Icon
                        name={theme !== 'dark' ? 'review_light.svg' : 'review.svg'}
                        className={styles.icon}
                    />
                </Link>

                <h2>Similar Movies</h2>
                {similarError || similarMovies.length === 0 ? (
                    <p>No similar movies found.</p>
                ) : (
                    <MovieGrid movies={similarMovies} />
                )}
            </main>
        </div>
    );
}

export default MoviePage;
