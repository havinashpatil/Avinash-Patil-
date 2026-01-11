/**
 * API Service for Blood Sense AI
 * Handles all HTTP requests to the backend API
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// ==================== Auth API ====================

export const authAPI = {
    login: async (username, password) => {
        const response = await apiClient.post('/api/auth/login', { username, password });
        return response.data;
    },

    register: async (userData) => {
        const response = await apiClient.post('/api/auth/register', userData);
        return response.data;
    },

    getMe: async () => {
        const response = await apiClient.get('/api/auth/me');
        return response.data;
    },
};

// ==================== Model API ====================

export const modelAPI = {
    health: async () => {
        const response = await apiClient.get('/api/model/health');
        return response.data;
    },

    metrics: async () => {
        const response = await apiClient.get('/api/model/metrics');
        return response.data;
    },

    info: async () => {
        const response = await apiClient.get('/api/model/info');
        return response.data;
    },
};

// ==================== Prediction API ====================

export const predictionAPI = {
    predictSingle: async (file, patientId, patientName) => {
        const formData = new FormData();
        formData.append('file', file);
        if (patientId) formData.append('patient_id', patientId);
        if (patientName) formData.append('patient_name', patientName);

        const response = await apiClient.post('/api/predict/single', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    predictBatch: async (files, patientId) => {
        const formData = new FormData();
        files.forEach((file) => {
            formData.append('files', file);
        });
        if (patientId) formData.append('patient_id', patientId);

        const response = await apiClient.post('/api/predict/batch', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    getPrediction: async (predictionId) => {
        const response = await apiClient.get(`/api/predictions/${predictionId}`);
        return response.data;
    },
};

// ==================== Scan API ====================

export const scanAPI = {
    getScans: async (params = {}) => {
        const response = await apiClient.get('/api/scans', { params });
        return response.data;
    },

    getScan: async (scanId) => {
        const response = await apiClient.get(`/api/scans/${scanId}`);
        return response.data;
    },

    updateScan: async (scanId, updates) => {
        const response = await apiClient.patch(`/api/scans/${scanId}`, updates);
        return response.data;
    },

    getPriorityScans: async (limit = 50) => {
        const response = await apiClient.get('/api/scans/priority', { params: { limit } });
        return response.data;
    },
};

// ==================== Report API ====================

export const reportAPI = {
    createReport: async (scanId, notes) => {
        const response = await apiClient.post('/api/reports', { scan_id: scanId, notes });
        return response.data;
    },

    getReport: async (scanId) => {
        const response = await apiClient.get(`/api/reports/${scanId}`);
        return response.data;
    },
};

// ==================== Statistics API ====================

export const statisticsAPI = {
    getStatistics: async () => {
        const response = await apiClient.get('/api/statistics');
        return response.data;
    },
};

// ==================== Health Check ====================

export const healthCheck = async () => {
    const response = await apiClient.get('/api/health');
    return response.data;
};

export default apiClient;
