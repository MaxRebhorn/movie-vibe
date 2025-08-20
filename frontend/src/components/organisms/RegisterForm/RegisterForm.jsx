// RegisterForm.jsx
import React, { useState } from 'react';
import AuthCard from '../../molecules/AuthCard/AuthCard';
import AuthForm from '../../molecules/AuthForm/AuthForm';
import styles from './RegisterForm.module.css';

function RegisterForm({ onSubmit }) {
    const [error, setError] = useState('');

    const handleSubmit = async (formData) => {
        setError('');
        try {
            await onSubmit(formData);
        } catch (error) {
            const errorMessage = error.message || 'Registration failed. Please try again.';
            setError(errorMessage);
            console.error('Registration error:', error);
        }
    };

    const registerFields = [
        {
            name: 'username',
            type: 'text',
            label: 'Username',
            placeholder: 'Choose a username',
            required: true
        },
        {
            name: 'email',
            type: 'email',
            label: 'Email',
            placeholder: 'Enter your email',
            required: true
        },
        {
            name: 'first_name',
            type: 'text',
            label: 'First Name',
            placeholder: 'Enter your first name (optional)',
            required: false
        },
        {
            name: 'last_name',
            type: 'text',
            label: 'Last Name',
            placeholder: 'Enter your last name (optional)',
            required: false
        },
        {
            name: 'password',
            type: 'password',
            label: 'Password',
            placeholder: 'Create a password',
            required: true
        },
        {
            name: 'password2',
            type: 'password',
            label: 'Confirm Password',
            placeholder: 'Confirm your password',
            required: true
        }
    ];

    return (
        <div className={styles.registerForm}>
            <AuthCard
                title="Create Account"
                subtitle="Join us to get started"
                footerText="Already have an account?"
                footerLinkText="Sign in"
                footerLinkPath="/login"
            >
                {error && <div className={styles.error}>{error}</div>}
                <AuthForm
                    fields={registerFields}
                    onSubmit={handleSubmit}
                    submitText="Create Account"
                />
            </AuthCard>
        </div>
    );
}

export default RegisterForm;