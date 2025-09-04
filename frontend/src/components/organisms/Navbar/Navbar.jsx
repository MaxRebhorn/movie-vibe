import React, { useEffect, useState, useContext } from 'react';
import Text from '../../atoms/Text/Text';
import Icon from '../../atoms/Icon/Icon';
import IconButton from '../../molecules/IconButton/IconButton';
import styles from './Navbar.module.css';
import { Link } from "react-router-dom";
import anim from "../../../styles/animation.module.css";
import { AuthContext } from "../../../context/AuthContext";

const Navbar = () => {
    const [theme, setTheme] = useState('dark');
    const { user } = useContext(AuthContext);

    // Debug: log the user every render
    console.log("Navbar render — user:", user);

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

    // Debug: log whenever the user changes
    useEffect(() => {
        console.log("AuthContext user updated:", user);
    }, [user]);

    return (
        <nav className={styles.navbar}>
            <div className={styles.logo}>
                <Link to={`/`} className={`
                    ${styles.linkWrapper}
                    ${anim.btnPress}
                    ${anim.hoverGlow}
                    ${anim.hoverZoom}
                `}>
                    <Icon name="logo.svg" alt="Logo"/>
                </Link>
            </div>
            <div className={styles.items}>
                <IconButton
                    name={theme === 'dark' ? 'sun.svg' : 'moon.svg'}
                    alt="Toggle theme"
                    onClick={toggleTheme}
                    className={styles.icon}
                />
                <Link to={`/user`} className={`
                    ${styles.linkWrapper}
                    ${anim.btnPress}
                    ${anim.hoverGlow}
                    ${anim.hoverZoom}
                `}>
                    <Icon name={theme !== 'dark' ? 'review_light.svg' : 'review.svg'} className={styles.icon}/>
                </Link>
                <Link to={`/user`} className={`
                    ${styles.linkWrapper}
                    ${anim.btnPress}
                    ${anim.hoverGlow}
                    ${anim.hoverZoom}
                `}>
                    <Icon name={theme !== 'dark' ? 'add_light.svg' : 'add.svg'} className={styles.icon}/>
                </Link>
                <Link to={user ? "/favorites" : "/login"} className={`
                    ${styles.linkWrapper}
                    ${anim.btnPress}
                    ${anim.hoverGlow}
                    ${anim.hoverZoom}
                `}>
                    <Icon name={theme !== 'dark' ? 'like_light.svg' : 'like.svg'} className={styles.icon}/>
                </Link>
                <Link to={user ? "/user" : "/login"} className={`
                    ${styles.linkWrapper}
                    ${anim.btnPress}
                    ${anim.hoverGlow}
                    ${anim.hoverZoom}
                `}>
                    {user ? (
                        <img
                            src={`https://api.dicebear.com/7.x/open-peeps/svg?seed=${encodeURIComponent(user.email)}`}
                            alt="User Avatar"
                            className={styles.icon}
                        />
                    ) : (
                        <Icon name={theme !== 'dark' ? 'user_light.svg' : 'user.svg'} className={styles.icon}/>
                    )}
                </Link>
            </div>
        </nav>
    );
};

export default Navbar;
