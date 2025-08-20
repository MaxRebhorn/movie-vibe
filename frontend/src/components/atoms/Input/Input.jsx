// Input.jsx (Atom Level)
import React from 'react';
import Text from '../Text/Text';
import styles from './Input.module.css';

function Input({ 
    type = 'text', 
    name, 
    label, 
    value, 
    onChange, 
    placeholder, 
    error, 
    required = false 
}) {
    return (
        <div className={styles.inputGroup}>
            {label && (
                <label htmlFor={name} className={styles.label}>
                    <Text variant="small" color="muted">
                        {label}
                        {required && <span className={styles.required}>*</span>}
                    </Text>
                </label>
            )}
            <input
                type={type}
                id={name}
                name={name}
                value={value}
                onChange={onChange}
                className={`${styles.input} ${error ? styles.error : ''}`}
                placeholder={placeholder}
                required={required}
            />
            {error && (
                <Text variant="extra-small" color="accent" className={styles.errorText}>
                    {error}
                </Text>
            )}
        </div>
    );
}

export default Input;