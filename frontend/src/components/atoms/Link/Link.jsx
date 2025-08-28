// Link.jsx (Atom Level)
import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import Text from '../Text/Text';
import styles from './Link.module.css';

function Link({ 
    to, 
    children, 
    size = 'md', 
    className = '', 
    ...props 
}) {
    return (
        <RouterLink
            to={to}
            className={`${styles.link} ${styles[size]} ${className}`}
            {...props}
        >
            <Text variant={size} color="accent">
                {children}
            </Text>
        </RouterLink>
    );
}

export default Link;