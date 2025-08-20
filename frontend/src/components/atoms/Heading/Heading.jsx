// Heading.jsx (Atom Level)
import React from 'react';
import Text from '../Text/Text';
import styles from './Heading.module.css';

function Heading({ level = 1, children, className = '' }) {
    const variant = `hero`;
    
    return (
        <Text variant={variant} className={`${styles.heading} ${styles[`level${level}`]} ${className}`}>
            {children}
        </Text>
    );
}

export default Heading;