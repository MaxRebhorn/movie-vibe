import React from 'react';
import Navbar from '../components/organisms/Navbar';
import SearchSection from '../components/organisms/SearchSection';
import MovieGrid from '../components/organisms/MovieGrid';
import '../styles/colors.css';
import '../styles/global.css';
import { useState } from 'react';

function LandingPage() {
  const [movies, setMovies] = useState([]);

  const handleSearch = async (query) => {
    console.log("Searching for:", query); // test first

    // later we'll fetch from backend
    // const res = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
    // const data = await res.json();
    // setMovies(data.results);

    // For now: mock result
    setMovies([{ id: 1, title: query, year: 2025 }]);
  };

  return (
    <div className="landing-page">
      <Navbar />
      <main className="main-container">
        <SearchSection onSearch={handleSearch} />
        <MovieGrid movies={movies} />
      </main>
    </div>
  );
}

export default LandingPage;
