import React from 'react';
import Text from '../atoms/Text';
import Button from '../atoms/Button';
import Icon from '../atoms/Icon';
import '../../styles/colors.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar__logo">
        <Icon name="logo.svg" alt="Logo" className="navbar__icon" />
      </div>
      <div className="navbar__items">
        <Text variant="menu" className="navbar__item">Page</Text>
        <Text variant="menu" className="navbar__item">Page</Text>
        <Text variant="menu" className="navbar__item">Page</Text>
        <Button className="navbar__button">Button</Button>
      </div>
    </nav>
  );
};

export default Navbar;