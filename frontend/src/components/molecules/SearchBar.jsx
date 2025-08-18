import { Text } from '../atoms/Text';
import { Button } from '../atoms/Button';

export const SearchBar = ({ placeholder = "Search movies..." }) => {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      border: '1px solid #ccc',
      borderRadius: '0.375rem',
      overflow: 'hidden',
      width: '100%',
      maxWidth: '500px'
    }}>
      <input
        type="text"
        placeholder={placeholder}
        style={{
          flex: 1,
          padding: '0.5rem 1rem',
          border: 'none',
          outline: 'none',
          fontSize: '1rem'
        }}
      />
      <Button style={{
        backgroundColor: '#007bff',
        color: 'white',
        padding: '0.5rem 1rem',
        border: 'none',
        cursor: 'pointer',
        transition: 'background-color 0.2s'
      }}
        onMouseEnter={e => e.currentTarget.style.backgroundColor = '#0056b3'}
        onMouseLeave={e => e.currentTarget.style.backgroundColor = '#007bff'}
      >
        <Text>Search</Text>
      </Button>
    </div>
  );
};
