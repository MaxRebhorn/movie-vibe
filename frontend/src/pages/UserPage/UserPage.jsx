import React, {useState, useEffect, useContext} from 'react';
import {useNavigate} from 'react-router-dom';
import Navbar from '../../components/organisms/Navbar/Navbar';
import UserProfile from '../../components/organisms/UserProfile/UserProfile';
import MovieGrid from "../../components/organisms/MovieGrid/MovieGrid";
import styles from './UserPage.module.css';
import {AuthContext} from '../../context/AuthContext';
import {favoriteAPI, recommendationAPI} from '../../services/api';

function UserPage() {
    const {user} = useContext(AuthContext);
    const navigate = useNavigate();

    const [favoriteMovies, setFavoriteMovies] = useState([]);
    const [recommendedMovies, setRecommendedMovies] = useState([]);
    const [loadingFavorites, setLoadingFavorites] = useState(true);
    const [loadingRecommended, setLoadingRecommended] = useState(true);
    const [errorFavorites, setErrorFavorites] = useState(null);
    const [errorRecommended, setErrorRecommended] = useState(null);

    // Redirect to login if no user
    useEffect(() => {
        if (!user) {
            navigate('/login');
        }
    }, [user, navigate]);

    // Fetch favorites and recommendations together
    useEffect(() => {
        if (!user) return;

        const fetchRecommendations = async () => {
            try {
                const data = await recommendationAPI.getRecommendations();
                setRecommendedMovies(data);
            } catch (err) {
                setErrorRecommended(err.message);
            } finally {
                setLoadingRecommended(false);
            }
        };

        fetchRecommendations();
    }, [user]);


    if (!user) return null; // render nothing while redirecting

    return (
        <div className={styles.container}>
            <Navbar/>
            <main className={styles.main}>
                <UserProfile
                    username={user.username}
                    profilepicture={user.profilepicture}
                    rank={user.rank}
                    reviews_written={user.reviews_written}
                    movies_watched={user.movies_watched}
                    movies_added={user.movies_added}
                />

                <section>
                    <h2>Your Favorites</h2>
                    {loadingFavorites ? (
                        <p>Loading favorites...</p>
                    ) : errorFavorites ? (
                        <p>Error loading favorites: {errorFavorites}</p>
                    ) : favoriteMovies.length === 0 ? (
                        <p>No favorite movies yet.</p>
                    ) : (
                        <MovieGrid movies={favoriteMovies}/>
                    )}
                </section>

                <section>
                    <h2>You Might Like These Movies Based on Your Likes</h2>
                    {loadingRecommended ? (
                        <p>Loading recommendations...</p>
                    ) : errorRecommended ? (
                        <p>Error loading recommendations: {errorRecommended}</p>
                    ) : recommendedMovies.length === 0 ? (
                        <p>No recommendations found.</p>
                    ) : (
                        <MovieGrid movies={recommendedMovies}/>
                    )}
                </section>
            </main>
        </div>
    );
}

export default UserPage;