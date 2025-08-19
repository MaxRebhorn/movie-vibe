import React, {useEffect, useState} from 'react';
import Text from '../../atoms/Text/Text';
import Icon from '../../atoms/Icon/Icon';
import IconButton from '../../molecules/IconButton/IconButton';
import styles from './Navbar.module.css';
import {Link} from "react-router-dom";


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
        <nav className={styles.navbar}>
            <div className={styles.logo}>
                <Link to={`/`} className={styles.linkWrapper}>
                    <Icon name="logo.svg" alt="Logo" className={styles.icon}/></Link>
            </div>
            <div className={styles.items}>
                <Text variant="menu" className={styles.item}>Page</Text>
                <Text variant="menu" className={styles.item}>Page</Text>
                <Text variant="menu" className={styles.item}>Page</Text>
                <Icon name={theme === 'dark' ? 'user_light.svg' : 'user_dark.svg'}></Icon>
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
