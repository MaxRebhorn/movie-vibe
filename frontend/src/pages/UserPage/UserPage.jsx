import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../../components/organisms/Navbar/Navbar';
import UserProfile from '../../components/organisms/UserProfile/UserProfile';
import MovieGrid from "../../components/organisms/MovieGrid/MovieGrid";
import styles from './UserPage.module.css';

function UserPage() {
    const { userId } = useParams();
    const navigate = useNavigate();

    // state for user data
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // state for recommended movies
    const [similarMovies, setSimilarMovies] = useState([]);
    const [similarError, setSimilarError] = useState(null);

    useEffect(() => {
        // check if user is logged in
        const authToken = localStorage.getItem('authToken'); // or your login state
        if (!authToken) {
            navigate('/login'); // redirect to login if not logged in
            return;
        }

        const fetchUser = async () => {
            try {
                const res = await fetch(`/api/users/${userId}`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                if (!res.ok) throw new Error("Failed to load user");
                const data = await res.json();
                setUser(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        const fetchRecommendations = async () => {
            try {
                const res = await fetch(`/api/users/${userId}/recommendations`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                if (!res.ok) throw new Error("Failed to load recommendations");
                const data = await res.json();
                setSimilarMovies(data);
            } catch (err) {
                setSimilarError(err.message);
            }
        };

        fetchUser();
        fetchRecommendations();
    }, [userId, navigate]);

    if (loading) return <p>Loading...</p>;
    if (error) return <p>{error}</p>;

    return (
        <div className={styles.container}>
            <Navbar />
            <main className={styles.main}>
                {user && (
                    <UserProfile
                        username={user.username}
                        profilepicture={user.profilepicture}
                        rank={user.rank}
                        reviews_written={user.reviews_written}
                        movies_watched={user.movies_watched}
                        movies_added={user.movies_added}
                    />
                )}

                <h2>You Might Like these Movies based on your likes</h2>
                {similarError || similarMovies.length === 0 ? (
                    <p>No similar movies found.</p>
                ) : (
                    <MovieGrid movies={similarMovies} />
                )}
            </main>
        </div>
    );
}

export default UserPage;
