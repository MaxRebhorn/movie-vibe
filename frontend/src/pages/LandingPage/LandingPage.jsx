import React, {useState} from 'react';
import Navbar from '../../components/organisms/Navbar/Navbar';
import SearchSection from '../../components/organisms/SearchSection/SearchSection';
import MovieGrid from '../../components/organisms/MovieGrid/MovieGrid';
import styles from './LandingPage.module.css';

function LandingPage() {
    const [movies, setMovies] = useState([]);

    const handleSearch = async (query) => {
        if (!query) return; // don't search empty query
        try {
            console.log("Searching for:", query); // debug
            const res = await fetch(`http://localhost:8000/api/movies/search/?q=${encodeURIComponent(query)}`);

            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

            const data = await res.json();
            console.log("Search result:", data); // debug

            // If backend returns { movies: [...] } adjust accordingly
            setMovies(data.movies || data);
        } catch (err) {
            console.error("Search failed:", err);
        }
    };

    return (
        <div className={styles.container}>
            <Navbar/>
            <main className={styles.main}>
                <SearchSection onSearch={handleSearch}/>
                <MovieGrid movies={movies}/>
            </main>
        </div>
    );
}

export default LandingPage;
