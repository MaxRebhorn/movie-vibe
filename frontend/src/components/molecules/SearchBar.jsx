import React from 'react';
import Text from '../atoms/Text';
import Icon from '../atoms/Icon';
import '../../styles/colors.css';

const SearchBar = () => {
  return (
    <div className="search-bar">
      <Text variant="placeholder">Search for a Movie</Text>
      <Icon name="icon-50.svg" alt="Search icon" className="search-icon" />
    </div>
  );
};

export default SearchBar;