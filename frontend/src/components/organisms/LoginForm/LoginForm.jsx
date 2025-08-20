// LoginForm.jsx (Organism Level)
import React from 'react';
import AuthCard from '../../molecules/AuthCard/AuthCard';
import AuthForm from '../../molecules/AuthForm/AuthForm';
import styles from './LoginForm.module.css';

function LoginForm({ onSubmit }) {
    const loginFields = [
        {
            name: 'username',
            type: 'text',
            label: 'Username or Email',
            placeholder: 'Enter your username or email',
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
                <AuthForm
                    fields={loginFields}
                    onSubmit={onSubmit}
                    submitText="Sign In"
                />
            </AuthCard>
        </div>
    );
}

export default LoginForm;