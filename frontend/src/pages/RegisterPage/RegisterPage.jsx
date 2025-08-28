// RegisterPage.jsx
import React, {useState} from 'react';
import Navbar from '../../components/organisms/Navbar/Navbar';
import RegisterForm from '../../components/organisms/RegisterForm/RegisterForm';
import {authAPI} from '../../services/api';
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

            // ✅ Check if registration was successful based on returned fields
            if (response.username) {
                setDebugInfo(prev => prev + '\nRegistration successful! Redirecting...');
                window.location.href = '/login';
            } else {
                throw new Error('Registration failed');
            }

        } catch (error) {
            console.error('Registration failed:', error);
            let fullError = typeof error === 'object' && error !== null
                ? JSON.stringify(error, null, 2)
                : error.message || String(error);
            setError('Registration failed');
            setDebugInfo(prev => prev + `\nError details:\n${fullError}`);
        }
    };

    return (
        <div className={styles.registerPage}>
            <Navbar/>
            <main className={styles.main}>
                <div className={styles.container}>
                    <div className={styles.debugPanel}>
                        <h3>Debug Information:</h3>
                        <pre>{debugInfo}</pre>
                    </div>
                    {error && <div className={styles.error}>{error}</div>}
                    <RegisterForm onSubmit={handleRegister}/>
                </div>
            </main>
        </div>
    );
}

export default RegisterPage;
