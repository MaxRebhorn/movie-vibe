// LoginPage.jsx (Page Level)
import React from 'react';
import Navbar from '../../components/organisms/Navbar/Navbar';
import LoginForm from '../../components/organisms/LoginForm/LoginForm';
import styles from './LoginPage.module.css';

function LoginPage() {
    const handleLogin = (formData) => {
        console.log('Login attempted with:', formData);
        // API call would go here
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