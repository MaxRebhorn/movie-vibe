import { Text } from '../atoms/Text';
import { Button } from '../atoms/Button'; // optional if you want hover behavior

export const NavItem = ({ children }) => {
  return (
    <div style={{
      padding: '0.5rem 1rem',
      cursor: 'pointer',
      borderRadius: '0.375rem',
      transition: 'background-color 0.2s'
    }}
      onMouseEnter={e => e.currentTarget.style.backgroundColor = '#f0f0f0'}
      onMouseLeave={e => e.currentTarget.style.backgroundColor = 'transparent'}
    >
      <Text>{children}</Text>
    </div>
  );
};
