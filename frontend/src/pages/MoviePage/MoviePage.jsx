import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Navbar from '../../components/organisms/Navbar/Navbar';
import MovieProfile from '../../components/organisms/MovieProfile/MovieProfile';
import MovieGrid from "../../components/organisms/MovieGrid/MovieGrid";
import styles from './MoviePage.module.css';

function MoviePage() {
    const { id } = useParams();
    const [movie, setMovie] = useState(null);
    const [similarMovies, setSimilarMovies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [similarError, setSimilarError] = useState(false);

    useEffect(() => {
        async function fetchMovieAndSimilar() {
            setLoading(true);
            try {
                // Fetch main movie
                const movieResponse = await fetch(`http://localhost:8000/api/movies/${id}/`);
                if (!movieResponse.ok) throw new Error("Failed to fetch movie details");
                const movieData = await movieResponse.json();
                setMovie(movieData);

                // Fetch similar movies
                try {
                    const similarResponse = await fetch(`http://localhost:8000/api/movies/${id}/similar/`);
                    if (!similarResponse.ok) throw new Error("Failed to fetch similar movies");
                    const similarData = await similarResponse.json();
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
            <Navbar/>
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

                <h2>Similar Movies</h2>
                {similarError || similarMovies.length === 0 ? (
                    <p>No similar movies found.</p>
                ) : (
                    <MovieGrid movies={similarMovies}/>
                )}
            </main>
        </div>
    );
}

export default MoviePage;
