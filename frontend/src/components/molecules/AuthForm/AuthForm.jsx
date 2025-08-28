// AuthForm.jsx (Molecule Level - Updated)
import React, { useState } from 'react';
import Input from '../../atoms/Input/Input';
import Button from '../../atoms/Button/Button';
import styles from './AuthForm.module.css';
import Text from '../../atoms/Text/Text'

function AuthForm({ fields, onSubmit, submitText }) {
    const [formData, setFormData] = useState(
        fields.reduce((acc, field) => {
            acc[field.name] = '';
            return acc;
        }, {})
    );
    const [errors, setErrors] = useState({});
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));

        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    const validateForm = () => {
        const newErrors = {};

        fields.forEach(field => {
            if (field.required && !formData[field.name].trim()) {
                newErrors[field.name] = `${field.label} is required`;
            }

            if (field.type === 'email' && formData[field.name]) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(formData[field.name])) {
                    newErrors[field.name] = 'Please enter a valid email address';
                }
            }

            if (field.name === 'password' && formData[field.name].length < 6) {
                newErrors[field.name] = 'Password must be at least 6 characters';
            }

            // Add password confirmation validation
            if (field.name === 'confirmPassword' && formData[field.name] !== formData.password) {
                newErrors[field.name] = 'Passwords do not match';
            }
        });

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (validateForm()) {
            setIsLoading(true);
            try {
                // Remove confirmPassword from data sent to API
                const { confirmPassword, ...submitData } = formData;
                await onSubmit(submitData);
            } catch (error) {
                console.error('Form submission error:', error);
                // Handle API errors here
                setErrors({ general: error.message || 'Registration failed' });
            } finally {
                setIsLoading(false);
            }
        }
    };

    return (
        <form className={styles.authForm} onSubmit={handleSubmit}>
            {fields.map(field => (
                <div key={field.name} className={styles.field}>
                    <Input
                        type={field.type}
                        name={field.name}
                        label={field.label}
                        value={formData[field.name]}
                        onChange={handleChange}
                        placeholder={field.placeholder}
                        error={errors[field.name]}
                        required={field.required}
                    />
                </div>
            ))}

            {errors.general && (
                <div className={styles.errorGeneral}>
                    <Text variant="extra-small" color="accent">
                        {errors.general}
                    </Text>
                </div>
            )}

            <Button
                type="submit"
                variant="primary"
                fullWidth
                loading={isLoading}
                className={styles.submit}
            >
                {submitText}
            </Button>
        </form>
    );
}

export default AuthForm;