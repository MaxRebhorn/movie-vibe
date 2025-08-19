import React, { useEffect, useState } from 'react';
import Text from '../atoms/Text';
import Button from '../atoms/Button';
import Icon from '../atoms/Icon';
import IconButton from '../molecules/IconButton';
import '../../styles/colors.css';

const Navbar = () => {
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  };

  return (
    <nav className="navbar">
      <div className="navbar__logo">
        <Icon name="logo.svg" alt="Logo" className="navbar__icon" />
      </div>
      <div className="navbar__items">
        <Text variant="menu" className="navbar__item">Page</Text>
        <Text variant="menu" className="navbar__item">Page</Text>
        <Text variant="menu" className="navbar__item">Page</Text>
        <Icon name={theme === 'dark' ? 'user_light.svg' : 'user_dark.svg'}></Icon>

        {/* 🌙 / ☀️ Theme toggle */}
        <IconButton
          name={theme === 'dark' ? 'sun.svg' : 'moon.svg'}
          alt="Toggle theme"
          onClick={toggleTheme}
        />
      </div>
    </nav>
  );
};

export default Navbar;
