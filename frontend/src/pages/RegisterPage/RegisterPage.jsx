// RegisterPage.jsx
import React, { useState } from 'react';
import Navbar from '../../components/organisms/Navbar/Navbar';
import RegisterForm from '../../components/organisms/RegisterForm/RegisterForm';
import { authAPI } from '../../services/api';
import styles from './RegisterPage.module.css';

function RegisterPage() {
    const [debugInfo, setDebugInfo] = useState('');
    const [error, setError] = useState('');

    const handleRegister = async (formData) => {
        setDebugInfo('Starting registration process...');
        setError('');
        console.log('Register attempted with:', formData);

        try {
            setDebugInfo('Making API request...');
            const response = await authAPI.register(formData);
            console.log('Registration successful:', response);

            // Check if registration was successful
            if (response.id || response.detail === "User created successfully") {
                setDebugInfo(prev => prev + '\nRegistration successful! Redirecting...');
                window.location.href = '/login';
            } else {
                throw new Error(response.detail || 'Registration failed');
            }

        } catch (error) {
            console.error('Registration failed:', error);
            const errorMessage = error.message || 'Registration failed. Please try again.';
            setError(errorMessage);
            setDebugInfo(prev => prev + `\nError: ${errorMessage}`);

            // Check for specific error types
            if (error.message.includes('Failed to fetch')) {
                setDebugInfo(prev => prev + '\nThis is a network error. Check:\n1. Django server is running\n2. CORS is configured\n3. No browser extensions blocking requests');
            }
        }
    };

    return (
        <div className={styles.registerPage}>
            <Navbar />
            <main className={styles.main}>
                <div className={styles.container}>
                    <div className={styles.debugPanel}>
                        <h3>Debug Information:</h3>
                        <pre>{debugInfo}</pre>
                    </div>
                    {error && <div className={styles.error}>{error}</div>}
                    <RegisterForm onSubmit={handleRegister} />
                </div>
            </main>
        </div>
    );
}

export default RegisterPage;