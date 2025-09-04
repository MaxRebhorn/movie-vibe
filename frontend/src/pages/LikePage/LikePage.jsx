// File: src/pages/LikePage/LikePage.jsx
import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/organisms/Navbar/Navbar';
import UserProfile from '../../components/organisms/UserProfile/UserProfile';
import MovieGrid from "../../components/organisms/MovieGrid/MovieGrid";
import styles from './LikePage.module.css';
import { AuthContext } from '../../context/AuthContext';
import { movieAPI, favoriteAPI } from '../../services/api';

function LikePage() {
    const { user } = useContext(AuthContext); // Get current user from context
    const navigate = useNavigate();

    const [favoriteMovies, setFavoriteMovies] = useState([]);
    const [similarMovies, setSimilarMovies] = useState([]);
    const [loadingFavorites, setLoadingFavorites] = useState(true);
    const [loadingSimilar, setLoadingSimilar] = useState(true);
    const [errorFavorites, setErrorFavorites] = useState(null);
    const [errorSimilar, setErrorSimilar] = useState(null);

    // Fetch favorite movies
    useEffect(() => {
        if (!user) return;

        const fetchFavorites = async () => {
            try {
                const data = await favoriteAPI.getFavorites();
                setFavoriteMovies(data);
            } catch (err) {
                setErrorFavorites(err.message);
            } finally {
                setLoadingFavorites(false);
            }
        };

        fetchFavorites();
    }, [user]);

    // Fetch similar/recommended movies
    useEffect(() => {
        if (!user) {
            navigate('/login'); // redirect to login if no user
            return;
        }

        const fetchRecommendations = async () => {
            try {
                const data = await movieAPI.getSimilarMovies(user.id); // or use user preferences
                setSimilarMovies(data);
            } catch (err) {
                setErrorSimilar(err.message);
            } finally {
                setLoadingSimilar(false);
            }
        };

        fetchRecommendations();
    }, [user, navigate]);

    if (!user) return null; // nothing to render while redirecting

    return (
        <div className={styles.container}>
            <Navbar />
            <main className={styles.main}>
                <h2>Your Favorites</h2>
                {loadingFavorites ? (
                    <p>Loading favorites...</p>
                ) : errorFavorites || favoriteMovies.length === 0 ? (
                    <p>No favorite movies yet.</p>
                ) : (
                    <MovieGrid movies={favoriteMovies} />
                )}
            </main>
        </div>
    );
}

export default LikePage;
