// RegisterPage.jsx (Using correct endpoint)
import React from 'react';
import Navbar from '../../components/organisms/Navbar/Navbar';
import RegisterForm from '../../components/organisms/RegisterForm/RegisterForm';
import { authAPI } from '../../services/api';
import styles from './RegisterPage.module.css';

function RegisterPage() {
    const handleRegister = async (formData) => {
        try {
            console.log('Register attempted with:', formData);
            const response = await authAPI.register(formData);
            console.log('Registration successful:', response);

            // Redirect to login page
            window.location.href = '/login';

        } catch (error) {
            console.error('Registration failed:', error);
            // Pass the error to the form
            throw error;
        }
    };

    return (
        <div className={styles.registerPage}>
            <Navbar />
            <main className={styles.main}>
                <div className={styles.container}>
                    <RegisterForm onSubmit={handleRegister} />
                </div>
            </main>
        </div>
    );
}

export default RegisterPage;