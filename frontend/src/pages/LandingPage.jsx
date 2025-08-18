import React from 'react';
import Navbar from '../components/organisms/Navbar';
import SearchSection from '../components/organisms/SearchSection';
import MovieGrid from '../components/organisms/MovieGrid';
import '../styles/colors.css';
import '../styles/global.css';

function LandingPage() {
  return (
    <div className="landing-page">
      <Navbar />
      <main className="main-container">
        <SearchSection />
        <MovieGrid />
      </main>
    </div>
  );
}

export default LandingPage;
