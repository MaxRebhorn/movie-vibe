// File: src/pages/LoginPage/LoginPage.jsx
import React, {useContext} from 'react';
import Navbar from '../../components/organisms/Navbar/Navbar';
import LoginForm from '../../components/organisms/LoginForm/LoginForm';
import styles from './LoginPage.module.css';
import {AuthContext} from "../../context/AuthContext";
import {authAPI} from "../../services/api";

function LoginPage() {
    const {setUser} = useContext(AuthContext); // <-- correct usage inside component

    const handleLogin = async (formData) => {
        try {
            console.log('Login attempted with:', formData);
            const response = await authAPI.login(formData);
            console.log('Login successful:', response);

            // ✅ Adjust this based on your Django API response
            if (response.detail === "Logged in successfully") {
                // Suppose Django returns user + token
                const currentUser = await authAPI.checkAuth();
                setUser(currentUser);

                // Redirect
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
            <Navbar/>
            <main className={styles.main}>
                <div className={styles.container}>
                    <LoginForm onSubmit={handleLogin}/>
                </div>
            </main>
        </div>
    );
}

export default LoginPage;
