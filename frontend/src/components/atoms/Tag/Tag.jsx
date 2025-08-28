import React from 'react';
import Text from '../Text/Text';
import styles from './Tag.module.css';

const Tag = ({ label, color = 'primary', size = 'default' }) => {
  return (
    <div
      className={`${styles.tag} ${styles[color]} ${styles[size]}`}
    >
      <Text variant="extra-small" color="onPrimary">{label}</Text>
    </div>
  );
};

export default Tag;
