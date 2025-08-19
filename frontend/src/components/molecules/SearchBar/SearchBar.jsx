// frontend/src/components/organisms/SearchBar.jsx
import React, { useState } from 'react';
import Text from '../../atoms/Text/Text';
import Icon from '../../atoms/Icon/Icon';
import styles from './SearchBar.module.css';

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(query);
    }
  };

   return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search for a Movie"
        className={styles.input}
      />
      <button type="submit" className={styles.button}>
        <img
          src="/search.svg"
          alt="Search icon"
          className={styles.icon}
          style={{ color: 'var(--text-primary)' }}
        />
      </button>
    </form>
  );
};

export default SearchBar;