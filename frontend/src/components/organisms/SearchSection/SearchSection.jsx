import React from "react";
import SearchBar from "../../molecules/SearchBar/SearchBar";
import Text from "../../atoms/Text/Text";
import styles from './SearchSection.module.css';

const SearchSection = ({ onSearch }) => {
  return (
      <div className={styles.section}>
          <Text variant="hero">
              <span className="text-accent">Mo</span>
              <span>Vi</span>
          </Text>
          <SearchBar onSearch={onSearch}/>
      </div>
  );
};

export default SearchSection;
