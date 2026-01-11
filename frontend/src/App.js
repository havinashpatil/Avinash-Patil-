/**
 * Main App Component
 * Routing and authentication
 */
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import TechnicianDashboard from './pages/TechnicianDashboard';
import ClinicianDashboard from './pages/ClinicianDashboard';
import './index.css';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
    const { isAuthenticated, user, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="spinner"></div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (allowedRoles && !allowedRoles.includes(user?.role)) {
        return <Navigate to="/" replace />;
    }

    return children;
};

// Main App Routes
const AppRoutes = () => {
    const { isAuthenticated, user } = useAuth();

    return (
        <Routes>
            <Route path="/login" element={
                isAuthenticated ? (
                    user?.role === 'technician' ? <Navigate to="/technician" replace /> :
                        user?.role === 'clinician' ? <Navigate to="/clinician" replace /> :
                            <Navigate to="/" replace />
                ) : (
                    <Login />
                )
            } />

            <Route path="/technician" element={
                <ProtectedRoute allowedRoles={['technician']}>
                    <TechnicianDashboard />
                </ProtectedRoute>
            } />

            <Route path="/clinician" element={
                <ProtectedRoute allowedRoles={['clinician']}>
                    <ClinicianDashboard />
                </ProtectedRoute>
            } />

            <Route path="/" element={
                isAuthenticated ? (
                    user?.role === 'technician' ? <Navigate to="/technician" replace /> :
                        user?.role === 'clinician' ? <Navigate to="/clinician" replace /> :
                            <Navigate to="/login" replace />
                ) : (
                    <Navigate to="/login" replace />
                )
            } />
        </Routes>
    );
};

function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <AppRoutes />
            </BrowserRouter>
        </AuthProvider>
    );
}

export default App;
