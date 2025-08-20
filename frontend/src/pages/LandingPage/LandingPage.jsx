// LandingPage.jsx (Updated)
import React, {useState} from 'react';
import Navbar from '../../components/organisms/Navbar/Navbar';
import SearchSection from '../../components/organisms/SearchSection/SearchSection';
import MovieGrid from '../../components/organisms/MovieGrid/MovieGrid';
import { movieAPI } from '../../services/api'; // Import the service
import styles from './LandingPage.module.css';

function LandingPage() {
    const [movies, setMovies] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSearch = async (query) => {
        if (!query) return;
        
        setLoading(true);
        setError('');
        
        try {
            console.log("Searching for:", query);
            const data = await movieAPI.search(query);
            console.log("Search result:", data);
            
            // If backend returns { movies: [...] } adjust accordingly
            setMovies(data.movies || data);
        } catch (err) {
            console.error("Search failed:", err);
            setError(err.message || 'Search failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <Navbar/>
            <main className={styles.main}>
                <SearchSection onSearch={handleSearch} loading={loading} />
                {error && <div className={styles.error}>{error}</div>}
                <MovieGrid movies={movies}/>
            </main>
        </div>
    );
}

export default LandingPage;