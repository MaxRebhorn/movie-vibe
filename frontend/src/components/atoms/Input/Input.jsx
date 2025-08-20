// Input.jsx (Atom Level)
import React from 'react';
import Text from '../Text/Text';
import styles from './Input.module.css';
import anim from '../../../styles/animation.module.css'; // ✅ import animations

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
                placeholder={placeholder}
                required={required}
                // 👇 Apply animations here
                className={`
                    ${styles.input} 
                    ${anim.inputFocusGlow} 
                    ${error ? anim.shake : ''} 
                    ${error ? styles.error : ''}
                `}
            />
            {error && (
                <Text
                    variant="extra-small"
                    color="accent"
                    className={styles.errorText}
                >
                    {error}
                </Text>
            )}
        </div>
    );
}

export default Input;
