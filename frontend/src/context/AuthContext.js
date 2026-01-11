/**
 * Authentication Context
 * Manages user authentication state across the application
 */
import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is already logged in
        const savedUser = localStorage.getItem('user');
        const savedToken = localStorage.getItem('token');

        if (savedUser && savedToken) {
            setUser(JSON.parse(savedUser));
        }

        setLoading(false);
    }, []);

    const login = async (username, password) => {
        try {
            const response = await authAPI.login(username, password);

            if (response.success && response.data) {
                const { token, user } = response.data;

                // Save to localStorage
                localStorage.setItem('token', token);
                localStorage.setItem('user', JSON.stringify(user));

                setUser(user);
                return { success: true, user };
            } else {
                throw new Error(response.message || 'Login failed');
            }
        } catch (error) {
            const message = error.response?.data?.message || error.message || 'Login failed';
            return { success: false, error: message };
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
    };

    const register = async (username, password, role, email) => {
        try {
            const response = await authAPI.register({ username, password, role, email });

            if (response.success) {
                return { success: true };
            } else {
                throw new Error(response.message || 'Registration failed');
            }
        } catch (error) {
            const message = error.response?.data?.message || error.message || 'Registration failed';
            return { success: false, error: message };
        }
    };

    const value = {
        user,
        loading,
        login,
        logout,
        register,
        isAuthenticated: !!user,
        isTechnician: user?.role === 'technician',
        isClinician: user?.role === 'clinician',
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
