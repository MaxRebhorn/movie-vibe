// LoginPage.jsx
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

            // Check if login was actually successful
            if (response.detail === "Logged in successfully") {
                window.location.href = '/';
            } else {
                throw new Error(response.detail || 'Login failed');
            }

        } catch (error) {
            console.error('Login failed:', error);
            throw new Error(error.message || 'Login failed. Please try again.');
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