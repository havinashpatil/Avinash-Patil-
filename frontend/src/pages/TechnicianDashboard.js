/**
 * Technician Dashboard
 * Upload interface with real-time predictions and alerts
 */
import React, { useState, useEffect } from 'react';
import { FaUpload, FaBell, FaCheckCircle, FaExclamationTriangle } from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';
import { predictionAPI, scanAPI, modelAPI } from '../services/api';
import UploadZone from '../components/UploadZone';
import CellDistribution from '../components/CellDistribution';

const TechnicianDashboard = () => {
    const { user, logout } = useAuth();
    const [loading, setLoading] = useState(false);
    const [recentScans, setRecentScans] = useState([]);
    const [currentPrediction, setCurrentPrediction] = useState(null);
    const [alert, setAlert] = useState(null);
    const [modelInfo, setModelInfo] = useState(null);
    const [uploadMode, setUploadMode] = useState('single');
    const [patientId, setPatientId] = useState('');

    useEffect(() => {
        loadRecentScans();
        loadModelInfo();
    }, []);

    const loadRecentScans = async () => {
        try {
            const response = await scanAPI.getScans({ limit: 10 });
            if (response.success) {
                setRecentScans(response.data.scans);
            }
        } catch (error) {
            console.error('Error loading scans:', error);
        }
    };

    const loadModelInfo = async () => {
        try {
            const response = await modelAPI.info();
            if (response.success) {
                setModelInfo(response.data);
            }
        } catch (error) {
            console.error('Error loading model info:', error);
        }
    };

    const handleUpload = async (files) => {
        setLoading(true);
        setAlert(null);
        setCurrentPrediction(null);

        try {
            let response;

            if (uploadMode === 'single') {
                response = await predictionAPI.predictSingle(files, patientId);
            } else {
                response = await predictionAPI.predictBatch(files, patientId);
            }

            if (response.success) {
                setCurrentPrediction(response.data);

                // Check for high priority (malignant cells)
                const isHighPriority = uploadMode === 'single'
                    ? response.data.priority === 'high'
                    : response.data.summary.high_priority > 0;

                if (isHighPriority) {
                    setAlert({
                        type: 'danger',
                        title: '⚠️ MALIGNANT CELLS DETECTED',
                        message: uploadMode === 'single'
                            ? `Blast cells identified with ${response.data.confidence.toFixed(1)}% confidence. Immediate clinician review required.`
                            : `${response.data.summary.high_priority} scans flagged as high priority. Immediate review required.`
                    });

                    // Play alert sound (optional)
                    playAlertSound();
                } else {
                    setAlert({
                        type: 'success',
                        title: '✓ Analysis Complete',
                        message: 'Normal cells detected. Routine processing.'
                    });
                }

                // Refresh recent scans
                loadRecentScans();
            } else {
                setAlert({
                    type: 'danger',
                    title: 'Analysis Failed',
                    message: response.message || 'Error processing image'
                });
            }
        } catch (error) {
            setAlert({
                type: 'danger',
                title: 'Upload Error',
                message: error.response?.data?.message || 'Failed to process upload'
            });
        }

        setLoading(false);
    };

    const playAlertSound = () => {
        // Optional: Play alert sound
        const audio = new Audio('/alert.mp3');
        audio.play().catch(() => {
            // Ignore if audio not available
        });
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-neutral-50">
            {/* Header */}
            <div className="glass-card-hover mx-4 my-4 p-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold font-display text-neutral-800">
                            Technician Dashboard
                        </h1>
                        <p className="text-neutral-600 mt-1">
                            Welcome, {user?.username} • Upload & Analyze Blood Smears
                        </p>
                    </div>
                    <button onClick={logout} className="btn-outline">
                        Logout
                    </button>
                </div>

                {modelInfo && (
                    <div className="mt-4 p-3 bg-success-50 rounded-lg border border-success-200">
                        <div className="flex items-center gap-2">
                            <FaCheckCircle className="text-success-600" />
                            <span className="text-sm font-medium text-success-700">
                                Model Status: Active • Last trained: {modelInfo.last_trained || 'Unknown'}
                            </span>
                        </div>
                    </div>
                )}
            </div>

            {/* Main Content */}
            <div className="page-container">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Left Column - Upload */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Alert */}
                        {alert && (
                            <div className={`alert-${alert.type}`}>
                                <div className="flex items-start gap-3">
                                    {alert.type === 'danger' && <FaExclamationTriangle className="text-2xl flex-shrink-0 mt-1" />}
                                    {alert.type === 'success' && <FaCheckCircle className="text-2xl flex-shrink-0 mt-1" />}
                                    <div>
                                        <p className="font-bold text-lg mb-1">{alert.title}</p>
                                        <p>{alert.message}</p>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Upload Mode Selection */}
                        <div className="glass-card p-6">
                            <h2 className="text-xl font-semibold text-neutral-800 mb-4">Upload Blood Smear</h2>

                            <div className="flex gap-4 mb-4">
                                <button
                                    onClick={() => setUploadMode('single')}
                                    className={`flex-1 p-3 rounded-xl border-2 ${uploadMode === 'single' ? 'border-primary-500 bg-primary-50' : 'border-neutral-200'}`}
                                >
                                    <p className="font-semibold text-neutral-800">Single Image</p>
                                </button>
                                <button
                                    onClick={() => setUploadMode('batch')}
                                    className={`flex-1 p-3 rounded-xl border-2 ${uploadMode === 'batch' ? 'border-primary-500 bg-primary-50' : 'border-neutral-200'}`}
                                >
                                    <p className="font-semibold text-neutral-800">Batch Upload</p>
                                </button>
                            </div>

                            <div className="mb-4">
                                <label className="block text-sm font-medium text-neutral-700 mb-2">
                                    Patient ID (Optional)
                                </label>
                                <input
                                    type="text"
                                    value={patientId}
                                    onChange={(e) => setPatientId(e.target.value)}
                                    className="input-field"
                                    placeholder="Enter patient ID"
                                />
                            </div>

                            <UploadZone onUpload={handleUpload} loading={loading} mode={uploadMode} />
                        </div>

                        {/* Prediction Results */}
                        {currentPrediction && uploadMode === 'single' && (
                            <CellDistribution probabilities={currentPrediction.all_probabilities} />
                        )}

                        {currentPrediction && uploadMode === 'batch' && (
                            <div className="glass-card p-6">
                                <h3 className="text-xl font-semibold text-neutral-800 mb-4">Batch Results</h3>

                                <div className="grid grid-cols-3 gap-4 mb-6">
                                    <div className="stat-card">
                                        <div className="stat-value">{currentPrediction.summary.total_images}</div>
                                        <div className="stat-label">Total Images</div>
                                    </div>
                                    <div className="stat-card">
                                        <div className="stat-value text-success-600">{currentPrediction.summary.successful}</div>
                                        <div className="stat-label">Successful</div>
                                    </div>
                                    <div className="stat-card">
                                        <div className="stat-value text-danger-600">{currentPrediction.summary.high_priority}</div>
                                        <div className="stat-label">High Priority</div>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    {currentPrediction.results.map((result, index) => (
                                        <div
                                            key={index}
                                            className={result.priority === 'high' ? 'card-priority-high p-4' : 'card-priority-normal p-4'}
                                        >
                                            <div className="flex items-center justify-between">
                                                <div>
                                                    <p className="font-semibold text-neutral-800">{result.filename}</p>
                                                    <p className="text-sm text-neutral-600 mt-1">
                                                        {result.predicted_class} • {result.confidence.toFixed(1)}% confidence
                                                    </p>
                                                </div>
                                                <div className={`badge-${result.priority === 'high' ? 'danger' : 'success'}`}>
                                                    {result.priority === 'high' ? 'HIGH PRIORITY' : 'NORMAL'}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Right Column - Recent Scans */}
                    <div className="space-y-6">
                        <div className="glass-card p-6">
                            <h3 className="text-lg font-semibold text-neutral-800 mb-4">Recent Scans</h3>

                            {recentScans.length === 0 ? (
                                <p className="text-neutral-500 text-center py-8">No scans yet</p>
                            ) : (
                                <div className="space-y-3">
                                    {recentScans.map((scan) => (
                                        <div
                                            key={scan._id}
                                            className={`p-3 rounded-lg border ${scan.priority === 'high' ? 'bg-danger-50 border-danger-200' : 'bg-neutral-50 border-neutral-200'}`}
                                        >
                                            <div className="flex items-start justify-between">
                                                <div>
                                                    <div className="flex items-center gap-2">
                                                        <span className="text-xs text-neutral-500">
                                                            {new Date(scan.created_at).toLocaleString()}
                                                        </span>
                                                    </div>
                                                    {scan.prediction && (
                                                        <p className="text-sm font-medium text-neutral-800 mt-1">
                                                            {scan.prediction.predicted_class}
                                                        </p>
                                                    )}
                                                </div>
                                                <div className={`badge-${scan.priority === 'high' ? 'danger' : 'success'} text-xs`}>
                                                    {scan.status}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TechnicianDashboard;
