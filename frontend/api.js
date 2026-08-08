// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Token Management
const getToken = () => localStorage.getItem('token');
const setToken = (token) => localStorage.setItem('token', token);
const clearToken = () => localStorage.removeItem('token');
const getCurrentUser = () => JSON.parse(localStorage.getItem('user') || 'null');
const setCurrentUser = (user) => localStorage.setItem('user', JSON.stringify(user));
const clearCurrentUser = () => localStorage.removeItem('user');

// API Helper Function
async function apiCall(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers
    };

    // Don't set Content-Type for FormData
    if (options.body instanceof FormData) {
        delete headers['Content-Type'];
    }

    const config = {
        ...options,
        headers
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || 'Request failed');
    }

    return response.json();
}

// Auth API
const authAPI = {
    login: (email, password) => 
        apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        }),
    
    setupAdmin: (email, password, firstName, lastName) =>
        apiCall('/auth/setup-admin', {
            method: 'POST',
            body: JSON.stringify({ email, password, first_name: firstName, last_name: lastName })
        }),
    
    getMe: () => apiCall('/auth/me')
};

// Settings API
const settingsAPI = {
    get: () => apiCall('/settings'),
    
    update: (data) =>
        apiCall('/settings', {
            method: 'PUT',
            body: JSON.stringify(data)
        })
};

// Users API
const usersAPI = {
    list: () => apiCall('/users'),
    
    create: (email, password, role, firstName, lastName) =>
        apiCall('/users', {
            method: 'POST',
            body: JSON.stringify({
                email,
                password,
                role,
                first_name: firstName,
                last_name: lastName
            })
        }),
    
    update: (userId, data) =>
        apiCall(`/users/${userId}`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        })
};

// Pipelines API
const pipelinesAPI = {
    list: () => apiCall('/pipelines'),
    
    create: (name, stages, isDefault = false) =>
        apiCall('/pipelines', {
            method: 'POST',
            body: JSON.stringify({
                name,
                is_default: isDefault,
                stages: stages.map((stage, index) => ({
                    name: stage,
                    order_index: index
                }))
            })
        })
};

// Jobs API
const jobsAPI = {
    create: (data) =>
        apiCall('/jobs', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
    
    update: (jobId, data) =>
        apiCall(`/jobs/${jobId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }),
    
    updateStatus: (jobId, status) =>
        apiCall(`/jobs/${jobId}/status`, {
            method: 'PATCH',
            body: JSON.stringify({ status })
        }),
    
    updateQuestions: (jobId, questions) =>
        apiCall(`/jobs/${jobId}/questions`, {
            method: 'PUT',
            body: JSON.stringify({ questions })
        }),
    
    createTrackingLink: (jobId, sourceName) =>
        apiCall(`/jobs/${jobId}/tracking-links`, {
            method: 'POST',
            body: JSON.stringify({ source_name: sourceName })
        }),
    
    getStats: (jobId) => apiCall(`/jobs/${jobId}/stats`)
};

// Public API
const publicAPI = {
    getJobs: (filters = {}) => {
        const params = new URLSearchParams(filters);
        return apiCall(`/public/jobs?${params}`);
    },
    
    getJob: (jobId) => apiCall(`/public/jobs/${jobId}`),
    
    apply: (jobId, formData) =>
        apiCall(`/public/jobs/${jobId}/apply`, {
            method: 'POST',
            body: formData
        })
};

// Applications API
const applicationsAPI = {
    list: (filters = {}) => {
        const params = new URLSearchParams(filters);
        return apiCall(`/applications?${params}`);
    },
    
    get: (applicationId) => apiCall(`/applications/${applicationId}`),
    
    moveStage: (applicationId, stageId) =>
        apiCall(`/applications/${applicationId}/stage`, {
            method: 'PATCH',
            body: JSON.stringify({ stage_id: stageId })
        }),
    
    vote: (applicationId, voteValue) =>
        apiCall(`/applications/${applicationId}/vote`, {
            method: 'POST',
            body: JSON.stringify({ vote_value: voteValue })
        }),
    
    comment: (applicationId, content) =>
        apiCall(`/applications/${applicationId}/comment`, {
            method: 'POST',
            body: JSON.stringify({ content })
        }),
    
    reanalyze: (applicationId) =>
        apiCall(`/applications/${applicationId}/re-analyze`, {
            method: 'POST'
        })
};
