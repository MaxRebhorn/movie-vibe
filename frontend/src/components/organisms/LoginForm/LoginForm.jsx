// LoginForm.jsx
import React, { useState } from 'react';
import AuthCard from '../../molecules/AuthCard/AuthCard';
import AuthForm from '../../molecules/AuthForm/AuthForm';
import styles from './LoginForm.module.css';

function LoginForm({ onSubmit }) {
    const [error, setError] = useState('');

    const handleLogin = async (formData) => {
        setError('');
        try {
            await onSubmit(formData);
        } catch (error) {
            const errorMessage = error.message || 'Login failed. Please check your credentials and try again.';
            setError(errorMessage);
            console.error('Login error:', error);
        }
    };

    const loginFields = [
        {
            name: 'username',
            type: 'text',
            label: 'Username',
            placeholder: 'Enter your username',
            required: true
        },
        {
            name: 'password',
            type: 'password',
            label: 'Password',
            placeholder: 'Enter your password',
            required: true
        }
    ];

    return (
        <div className={styles.loginForm}>
            <AuthCard
                title="Welcome Back"
                subtitle="Please sign in to your account"
                footerText="Don't have an account?"
                footerLinkText="Sign up"
                footerLinkPath="/register"
            >
                {error && <div className={styles.error}>{error}</div>}
                <AuthForm
                    fields={loginFields}
                    onSubmit={handleLogin}
                    submitText="Sign In"
                />
            </AuthCard>
        </div>
    );
}

export default LoginForm;