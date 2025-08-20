// RegisterPage.jsx (Page Level)
import React from 'react';
import Navbar from '../../components/organisms/Navbar/Navbar';
import RegisterForm from '../../components/organisms/RegisterForm/RegisterForm';
import styles from './RegisterPage.module.css';

function RegisterPage() {
    const handleRegister = (formData) => {
        console.log('Register attempted with:', formData);
        // API call would go here
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