// frontend/src/components/organisms/SearchBar.jsx
import React, { useState } from 'react';
import Text from '../atoms/Text';
import Icon from '../atoms/Icon';
import '../../styles/colors.css';
import '../../styles/global.css';

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(query);
    }
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      {/* Text input */}
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search for a Movie"
        className="search-input"
      />

      {/* Icon as button */}
      <button
        type="submit"
        className="search-button"
        style={{
          background: 'transparent',
          border: 'none',
          padding: 0,
          cursor: 'pointer'
        }}
      >
        <Icon
          name="search.svg"
          alt="Search icon"
          className="search-icon"
          style={{ color: 'var(--text-primary)' }}
        />
      </button>
    </form>
  );
};

export default SearchBar;