// AuthCard.jsx (Molecule Level)
import React from 'react';
import Card from '../../atoms/Card/Card';
import Heading from '../../atoms/Heading/Heading';
import Text from '../../atoms/Text/Text';
import Link from '../../atoms/Link/Link';
import styles from './AuthCard.module.css';

function AuthCard({ title, subtitle, children, footerText, footerLinkText, footerLinkPath }) {
    return (
        <Card className={styles.authCard}>
            <div className={styles.header}>
                <Heading level={1} className={styles.title}>{title}</Heading>
                {subtitle && <Text className={styles.subtitle}>{subtitle}</Text>}
            </div>
            
            <div className={styles.body}>
                {children}
            </div>
            
            {(footerText || footerLinkText) && (
                <div className={styles.footer}>
                    {footerText && <Text size="sm" color="muted">{footerText}</Text>}
                    {footerLinkText && (
                        <Link to={footerLinkPath} size="sm" className={styles.link}>
                            {footerLinkText}
                        </Link>
                    )}
                </div>
            )}
        </Card>
    );
}

export default AuthCard;