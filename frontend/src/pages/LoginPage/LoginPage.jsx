// LoginPage.jsx (Using correct endpoint)
import React from 'react';
import Navbar from '../../components/organisms/Navbar/Navbar';
import LoginForm from '../../components/organisms/LoginForm/LoginForm';
import { authAPI } from '../../services/api';
import styles from './LoginPage.module.css';

function LoginPage() {
    const handleLogin = async (formData) => {
        try {
            console.log('Login attempted with:', formData);
            const response = await authAPI.login(formData);
            console.log('Login successful:', response);

            // Redirect to home page
            window.location.href = '/';

        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    };

    return (
        <div className={styles.loginPage}>
            <Navbar />
            <main className={styles.main}>
                <div className={styles.container}>
                    <LoginForm onSubmit={handleLogin} />
                </div>
            </main>
        </div>
    );
}

export default LoginPage;