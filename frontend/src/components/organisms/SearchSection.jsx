import React from 'react';
import Text from '../atoms/Text';
import SearchBar from '../molecules/SearchBar';
import '../../styles/colors.css';

const SearchSection = () => {
  return (
    <section className="search-section">
      <Text variant="hero">
        <span className="text-accent">Mo</span>
        <span>Vi</span>
      </Text>
      <SearchBar />
    </section>
  );
};

export default SearchSection;