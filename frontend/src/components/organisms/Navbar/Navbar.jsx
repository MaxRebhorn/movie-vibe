import React, {useEffect, useState} from 'react';
import Text from '../../atoms/Text/Text';
import Icon from '../../atoms/Icon/Icon';
import IconButton from '../../molecules/IconButton/IconButton';
import styles from './Navbar.module.css';
import {Link} from "react-router-dom";
import anim from "../../../styles/animation.module.css";


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
                <Link to={`/`} className={`
        ${styles.linkWrapper}
        ${anim.btnPress}
        ${anim.hoverGlow}
        ${anim.hoverZoom}
      `}>
                    <Icon name="logo.svg" alt="Logo"/></Link>
            </div>
            <div className={styles.items}>
                <IconButton
                    name={theme === 'dark' ? 'sun.svg' : 'moon.svg'}
                    alt="Toggle theme"
                    onClick={toggleTheme}
                    className={styles.icon}   // make sure IconButton passes this down to the Icon inside
                />
                <Link to={`/user`} className={`
        ${styles.linkWrapper}
        ${anim.btnPress}
        ${anim.hoverGlow}
        ${anim.hoverZoom}
      `}><Icon name={theme !== 'dark' ? 'review_light.svg' : 'review.svg'} className={styles.icon}/></Link>
                <Link to={`/user`} className={`
        ${styles.linkWrapper}
        ${anim.btnPress}
        ${anim.hoverGlow}
        ${anim.hoverZoom}
      `}> <Icon name={theme !== 'dark' ? 'add_light.svg' : 'add.svg'} className={styles.icon}/></Link>
                <Link to={`/user`} className={`
        ${styles.linkWrapper}
        ${anim.btnPress}
        ${anim.hoverGlow}
        ${anim.hoverZoom}
      `}><Icon name={theme !== 'dark' ? 'like_light.svg' : 'like.svg'} className={styles.icon}/></Link>
                <Link to={`/user`} className={`
        ${styles.linkWrapper}
        ${anim.btnPress}
        ${anim.hoverGlow}
        ${anim.hoverZoom}
      `}> <Icon name={theme !== 'dark' ? 'user_light.svg' : 'user.svg'} className={styles.icon}/></Link>
            </div>
        </nav>
    );
};

export default Navbar;
