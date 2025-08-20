// RegisterForm.jsx (Organism Level)
import React from 'react';
import AuthCard from '../../molecules/AuthCard/AuthCard';
import AuthForm from '../../molecules/AuthForm/AuthForm';
import styles from './RegisterForm.module.css';

function RegisterForm({ onSubmit }) {
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
            name: 'password',
            type: 'password',
            label: 'Password',
            placeholder: 'Create a password',
            required: true
        },
        {
            name: 'confirmPassword',
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
                <AuthForm
                    fields={registerFields}
                    onSubmit={onSubmit}
                    submitText="Create Account"
                />
            </AuthCard>
        </div>
    );
}

export default RegisterForm;