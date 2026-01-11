/**
 * Login Page Component
 * Premium authentication interface with role visualization
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FaUser, FaLock, FaMicroscope } from 'react-icons/fa';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const result = await login(username, password);

        if (result.success) {
            // Redirect based on role
            if (result.user.role === 'technician') {
                navigate('/technician');
            } else if (result.user.role === 'clinician') {
                navigate('/clinician');
            } else {
                navigate('/');
            }
        } else {
            setError(result.error);
        }

        setLoading(false);
    };

    const handleDemoLogin = async (role) => {
        const demoUsers = {
            technician: { username: 'tech_demo', password: 'demo123' },
            clinician: { username: 'doc_demo', password: 'demo123' }
        };

        const demo = demoUsers[role];
        setUsername(demo.username);
        setPassword(demo.password);

        setLoading(true);
        const result = await login(demo.username, demo.password);

        if (result.success) {
            navigate(role === 'technician' ? '/technician' : '/clinician');
        } else {
            setError(result.error);
        }

        setLoading(false);
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-primary-100 via-white to-success-100">
            <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-2 gap-8">

                {/* Branding Section */}
                <div className="glass-card p-12 flex flex-col justify-center animate-fade-in">
                    <div className="flex items-center gap-4 mb-8">
                        <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl flex items-center justify-center shadow-glow">
                            <FaMicroscope className="text-3xl text-white" />
                        </div>
                        <div>
                            <h1 className="text-4xl font-bold font-display text-neutral-800">
                                Blood Sense AI
                            </h1>
                            <p className="text-neutral-600 font-medium">Cancer Detection System</p>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div className="p-6 bg-gradient-to-r from-primary-50 to-primary-100 rounded-xl">
                            <h3 className="text-xl font-semibold text-primary-700 mb-2">
                                🎯 Objective Diagnosis
                            </h3>
                            <p className="text-neutral-700">
                                Replace manual microscopic counting with AI-powered objective analysis
                            </p>
                        </div>

                        <div className="p-6 bg-gradient-to-r from-success-50 to-success-100 rounded-xl">
                            <h3 className="text-xl font-semibold text-success-700 mb-2">
                                🔬 High Sensitivity
                            </h3>
                            <p className="text-neutral-700">
                                Maximized recall to ensure rare blast cells are never missed
                            </p>
                        </div>

                        <div className="p-6 bg-gradient-to-r from-danger-50 to-danger-100 rounded-xl">
                            <h3 className="text-xl font-semibold text-danger-700 mb-2">
                                ⚡ Rapid Triage
                            </h3>
                            <p className="text-neutral-700">
                                Instant malignancy alerts for urgent clinical review
                            </p>
                        </div>
                    </div>
                </div>

                {/* Login Form Sectionf */}
                <div className="glass-card p-12 animate-slide-up">
                    <h2 className="text-3xl font-bold font-display text-neutral-800 mb-2">
                        Welcome Back
                    </h2>
                    <p className="text-neutral-600 mb-8">Sign in to access the system</p>

                    {error && (
                        <div className="alert-danger mb-6">
                            <p className="font-medium">{error}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-neutral-700 mb-2">
                                Username
                            </label>
                            <div className="relative">
                                <FaUser className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400" />
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="input-field pl-12"
                                    placeholder="Enter your username"
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-neutral-700 mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <FaLock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400" />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="input-field pl-12"
                                    placeholder="Enter your password"
                                    required
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="btn-primary w-full text-lg"
                        >
                            {loading ? (
                                <span className="flex items-center justify-center gap-2">
                                    <span className="spinner"></span>
                                    Signing in...
                                </span>
                            ) : (
                                'Sign In'
                            )}
                        </button>
                    </form>

                    <div className="mt-8 pt-8 border-t border-neutral-200">
                        <p className="text-sm text-neutral-600 mb-4 text-center">
                            Quick demo access:
                        </p>
                        <div className="grid grid-cols-2 gap-4">
                            <button
                                onClick={() => handleDemoLogin('technician')}
                                disabled={loading}
                                className="p-4 bg-primary-50 border-2 border-primary-200 rounded-xl hover:bg-primary-100 hover:border-primary-400 transition-all duration-300"
                            >
                                <p className="font-semibold text-primary-700">Technician</p>
                                <p className="text-xs text-neutral-600 mt-1">Upload & Scan</p>
                            </button>

                            <button
                                onClick={() => handleDemoLogin('clinician')}
                                disabled={loading}
                                className="p-4 bg-success-50 border-2 border-success-200 rounded-xl hover:bg-success-100 hover:border-success-400 transition-all duration-300"
                            >
                                <p className="font-semibold text-success-700">Clinician</p>
                                <p className="text-xs text-neutral-600 mt-1">Review & Report</p>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
