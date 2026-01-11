/**
 * Clinician Dashboard
 * Priority queue, detailed analysis, and report generation
 */
import React, { useState, useEffect } from 'react';
import { FaCheckCircle, FaNotesMedical, FaExclamationTriangle } from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';
import { scanAPI, reportAPI, modelAPI } from '../services/api';
import CellDistribution from '../components/CellDistribution';
import RecallMetric from '../components/RecallMetric';

const ClinicianDashboard = () => {
    const { user, logout } = useAuth();
    const [priorityScans, setPriorityScans] = useState([]);
    const [allScans, setAllScans] = useState([]);
    const [selectedScan, setSelectedScan] = useState(null);
    const [notes, setNotes] = useState('');
    const [loading, setLoading] = useState(false);
    const [modelMetrics, setModelMetrics] = useState(null);
    const [activeTab, setActiveTab] = useState('priority');

    useEffect(() => {
        loadScans();
        loadModelMetrics();
    }, []);

    const loadScans = async () => {
        try {
            const [priorityRes, allRes] = await Promise.all([
                scanAPI.getPriorityScans(20),
                scanAPI.getScans({ limit: 50 })
            ]);

            if (priorityRes.success) {
                setPriorityScans(priorityRes.data.scans);
            }
            if (allRes.success) {
                setAllScans(allRes.data.scans);
            }
        } catch (error) {
            console.error('Error loading scans:', error);
        }
    };

    const loadModelMetrics = async () => {
        try {
            const response = await modelAPI.metrics();
            if (response.success) {
                setModelMetrics(response.data.metrics);
            }
        } catch (error) {
            console.error('Error loading metrics:', error);
        }
    };

    const handleSelectScan = async (scan) => {
        setSelectedScan(scan);
        setNotes('');

        // Load full scan details
        try {
            const response = await scanAPI.getScan(scan._id);
            if (response.success) {
                setSelectedScan(response.data.scan);
            }
        } catch (error) {
            console.error('Error loading scan details:', error);
        }
    };

    const handleCreateReport = async () => {
        if (!selectedScan) return;

        setLoading(true);
        try {
            const response = await reportAPI.createReport(selectedScan._id, notes);

            if (response.success) {
                alert('✅ Report created successfully!');
                setSelectedScan(null);
                setNotes('');
                loadScans(); // Refresh scans
            } else {
                alert('Error creating report: ' + response.message);
            }
        } catch (error) {
            alert('Error creating report: ' + (error.response?.data?.message || error.message));
        }
        setLoading(false);
    };

    const scansToDisplay = activeTab === 'priority' ? priorityScans : allScans;

    return (
        <div className="min-h-screen bg-gradient-to-br from-success-50 via-white to-neutral-50">
            {/* Header */}
            <div className="glass-card-hover mx-4 my-4 p-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold font-display text-neutral-800">
                            Clinician Dashboard
                        </h1>
                        <p className="text-neutral-600 mt-1">
                            Welcome, Dr. {user?.username} • Review & Diagnose
                        </p>
                    </div>
                    <button onClick={logout} className="btn-outline">
                        Logout
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="page-container">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Left Column - Scan Queue */}
                    <div className="space-y-6">
                        {/* Stats */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="stat-card">
                                <div className="stat-value text-danger-600">{priorityScans.length}</div>
                                <div className="stat-label">High Priority</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-value text-primary-600">{allScans.length}</div>
                                <div className="stat-label">Total Scans</div>
                            </div>
                        </div>

                        {/* Tab Selection */}
                        <div className="glass-card p-4">
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setActiveTab('priority')}
                                    className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${activeTab === 'priority'
                                            ? 'bg-danger-500 text-white'
                                            : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                                        }`}
                                >
                                    Priority Queue
                                </button>
                                <button
                                    onClick={() => setActiveTab('all')}
                                    className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${activeTab === 'all'
                                            ? 'bg-primary-500 text-white'
                                            : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                                        }`}
                                >
                                    All Scans
                                </button>
                            </div>
                        </div>

                        {/* Scan List */}
                        <div className="glass-card p-6 max-h-[600px] overflow-y-auto">
                            <h3 className="text-lg font-semibold text-neutral-800 mb-4">
                                {activeTab === 'priority' ? '⚠️ Priority Scans' : '📋 All Scans'}
                            </h3>

                            {scansToDisplay.length === 0 ? (
                                <p className="text-neutral-500 text-center py-8">
                                    {activeTab === 'priority' ? 'No priority scans' : 'No scans available'}
                                </p>
                            ) : (
                                <div className="space-y-3">
                                    {scansToDisplay.map((scan) => (
                                        <button
                                            key={scan._id}
                                            onClick={() => handleSelectScan(scan)}
                                            className={`w-full text-left p-4 rounded-lg border-2 transition-all ${selectedScan?._id === scan._id
                                                    ? 'border-primary-500 bg-primary-50'
                                                    : scan.priority === 'high'
                                                        ? 'border-danger-200 bg-danger-50 hover:border-danger-400'
                                                        : 'border-neutral-200 bg-white hover:border-primary-300'
                                                }`}
                                        >
                                            <div className="flex items-start justify-between mb-2">
                                                <div>
                                                    <p className="font-semibold text-neutral-800">
                                                        Patient: {scan.patient_id || 'Unknown'}
                                                    </p>
                                                    <p className="text-xs text-neutral-500 mt-1">
                                                        {new Date(scan.created_at).toLocaleString()}
                                                    </p>
                                                </div>
                                                {scan.priority === 'high' && (
                                                    <FaExclamationTriangle className="text-danger-500 text-xl" />
                                                )}
                                            </div>

                                            {scan.prediction && (
                                                <div className="mt-2">
                                                    <p className="text-sm font-medium text-neutral-700">
                                                        {scan.prediction.predicted_class}
                                                    </p>
                                                    <p className="text-xs text-neutral-500">
                                                        {(scan.prediction.confidence * 100).toFixed(1)}% confidence
                                                    </p>
                                                </div>
                                            )}

                                            <div className={`mt-2 badge-${scan.status === 'reviewed' ? 'success' : 'warning'}`}>
                                                {scan.status}
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right Column - Detailed View */}
                    <div className="lg:col-span-2 space-y-6">
                        {!selectedScan ? (
                            <div className="glass-card p-12 text-center">
                                <p className="text-neutral-500 text-lg">
                                    Select a scan from the queue to view details
                                </p>
                            </div>
                        ) : (
                            <>
                                {/* Scan Details */}
                                <div className="glass-card p-6">
                                    <div className="flex items-start justify-between mb-6">
                                        <div>
                                            <h2 className="text-2xl font-bold text-neutral-800">
                                                Scan Details
                                            </h2>
                                            <p className="text-neutral-600 mt-1">
                                                Patient ID: {selectedScan.patient_id || 'Unknown'}
                                            </p>
                                            <p className="text-sm text-neutral-500">
                                                Uploaded: {new Date(selectedScan.created_at).toLocaleString()}
                                            </p>
                                        </div>
                                        <div className={`badge-${selectedScan.priority === 'high' ? 'danger' : 'success'} text-lg`}>
                                            {selectedScan.priority === 'high' ? '⚠️ HIGH PRIORITY' : '✓ NORMAL'}
                                        </div>
                                    </div>

                                    {selectedScan.prediction && (
                                        <div className={`p-6 rounded-xl ${selectedScan.priority === 'high'
                                                ? 'bg-gradient-to-r from-danger-50 to-danger-100 border-2 border-danger-300'
                                                : 'bg-gradient-to-r from-success-50 to-success-100 border-2 border-success-300'
                                            }`}>
                                            <div className="grid grid-cols-2 gap-6">
                                                <div>
                                                    <p className="text-sm font-medium text-neutral-600 mb-1">Predicted Class</p>
                                                    <p className={`text-3xl font-bold ${selectedScan.priority === 'high' ? 'text-danger-700' : 'text-success-700'}`}>
                                                        {selectedScan.prediction.predicted_class}
                                                    </p>
                                                </div>
                                                <div>
                                                    <p className="text-sm font-medium text-neutral-600 mb-1">Confidence</p>
                                                    <p className={`text-3xl font-bold ${selectedScan.priority === 'high' ? 'text-danger-700' : 'text-success-700'}`}>
                                                        {(selectedScan.prediction.confidence * 100).toFixed(1)}%
                                                    </p>
                                                </div>
                                            </div>

                                            {selectedScan.prediction.recall_note && (
                                                <div className="mt-4 p-3 bg-white/50 rounded-lg">
                                                    <p className="text-sm text-neutral-700">
                                                        📊 {selectedScan.prediction.recall_note}
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>

                                {/* Cell Distribution */}
                                {selectedScan.prediction?.all_probabilities && (
                                    <CellDistribution probabilities={selectedScan.prediction.all_probabilities} />
                                )}

                                {/* Review & Report Section */}
                                <div className="glass-card p-6">
                                    <h3 className="text-xl font-semibold text-neutral-800 mb-4 flex items-center gap-2">
                                        <FaNotesMedical className="text-primary-500" />
                                        Clinical Review
                                    </h3>

                                    {selectedScan.report ? (
                                        <div className="alert-success">
                                            <p className="font-semibold mb-2">✓ Report Finalized</p>
                                            <p className="text-sm">
                                                Reviewed on: {new Date(selectedScan.report.finalized_at).toLocaleString()}
                                            </p>
                                            {selectedScan.report.notes && (
                                                <div className="mt-3 p-3 bg-white/50 rounded-lg">
                                                    <p className="text-sm font-medium mb-1">Clinical Notes:</p>
                                                    <p className="text-sm">{selectedScan.report.notes}</p>
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <>
                                            <div className="mb-4">
                                                <label className="block text-sm font-medium text-neutral-700 mb-2">
                                                    Clinical Notes
                                                </label>
                                                <textarea
                                                    value={notes}
                                                    onChange={(e) => setNotes(e.target.value)}
                                                    className="input-field min-h-[120px]"
                                                    placeholder="Enter your clinical observations and recommendations..."
                                                />
                                            </div>

                                            <button
                                                onClick={handleCreateReport}
                                                disabled={loading}
                                                className="btn-success w-full"
                                            >
                                                {loading ? (
                                                    <span className="flex items-center justify-center gap-2">
                                                        <span className="spinner"></span>
                                                        Creating Report...
                                                    </span>
                                                ) : (
                                                    <span className="flex items-center justify-center gap-2">
                                                        <FaCheckCircle />
                                                        Finalize Report
                                                    </span>
                                                )}
                                            </button>
                                        </>
                                    )}
                                </div>
                            </>
                        )}

                        {/* Model Metrics */}
                        {modelMetrics && (
                            <RecallMetric metrics={modelMetrics} />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ClinicianDashboard;
