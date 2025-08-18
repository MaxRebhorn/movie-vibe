import React from "react";
import SearchBar from "../molecules/SearchBar";
import Text from "../atoms/Text";

const SearchSection = ({ onSearch }) => {
  return (
    <div className="search-section">
        <Text variant="hero">
        <span className="text-accent">Mo</span>
        <span>Vi</span>
      </Text>
      <SearchBar onSearch={onSearch} />
    </div>
  );
};

export default SearchSection;
