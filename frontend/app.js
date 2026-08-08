// Application State
let currentUser = getCurrentUser();
let currentPage = 'login';
let currentPipelines = [];

// Router
const routes = {
    'login': renderLoginPage,
    'setup': renderSetupPage,
    'admin-dashboard': renderAdminDashboard,
    'recruiter-jobs': renderRecruiterJobs,
    'recruiter-form-builder': renderFormBuilder,
    'public-jobs': renderPublicJobs,
    'public-job-detail': renderJobDetail,
    'public-apply': renderApplicationForm,
    'reviewer-kanban': renderKanbanBoard,
    'reviewer-application': renderApplicationDetail,
    'candidate-dashboard': renderCandidateDashboard
};

function navigate(page, params = {}) {
    currentPage = page;
    window.scrollTo(0, 0);
    
    const renderFn = routes[page];
    if (renderFn) {
        renderFn(params);
    } else {
        showError('Page not found');
    }
}

// Navigation Rendering
function renderNavigation() {
    const navLinks = document.getElementById('nav-links');
    
    if (!currentUser) {
        navLinks.innerHTML = `
            <button onclick="navigate('login')">Login</button>
            <button onclick="navigate('public-jobs')" class="btn-secondary">Browse Jobs</button>
        `;
        return;
    }

    const links = [];
    
    if (currentUser.role === 'ADMIN' || currentUser.role === 'admin') {
        links.push('<button onclick="navigate(\'admin-dashboard\')">Admin Dashboard</button>');
    }
    
    if (currentUser.role === 'RECRUITER' || currentUser.role === 'recruiter' || currentUser.role === 'ADMIN' || currentUser.role === 'admin') {
        links.push('<button onclick="navigate(\'recruiter-jobs\')">Jobs</button>');
    }
    
    if (currentUser.role === 'REVIEWER' || currentUser.role === 'reviewer' || currentUser.role === 'ADMIN' || currentUser.role === 'admin') {
        links.push('<button onclick="navigate(\'reviewer-kanban\')">Applications</button>');
    }
    
    if (currentUser.role === 'CANDIDATE' || currentUser.role === 'candidate') {
        links.push('<button onclick="navigate(\'candidate-dashboard\')">My Applications</button>');
    }
    
    links.push('<button onclick="navigate(\'public-jobs\')" class="btn-secondary">Job Board</button>');
    links.push(`<span style="margin: 0 1rem; color: #666;">${currentUser.email}</span>`);
    links.push('<button onclick="logout()" class="btn-secondary">Logout</button>');
    
    navLinks.innerHTML = links.join('');
}

// Logout
function logout() {
    clearToken();
    clearCurrentUser();
    currentUser = null;
    navigate('login');
    renderNavigation();
}

// Utility Functions
function showError(message) {
    const content = document.getElementById('app-content');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    content.insertBefore(errorDiv, content.firstChild);
    
    setTimeout(() => errorDiv.remove(), 5000);
}

function showSuccess(message) {
    const content = document.getElementById('app-content');
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    content.insertBefore(successDiv, content.firstChild);
    
    setTimeout(() => successDiv.remove(), 3000);
}

function showLoading() {
    document.getElementById('app-content').innerHTML = '<div class="loading">Loading...</div>';
}

// Page Renderers (Stubs - will implement one by one)
function renderLoginPage() {
    const content = document.getElementById('app-content');
    content.innerHTML = `
        <div class="card" style="max-width: 400px; margin: 2rem auto;">
            <h2>Login</h2>
            <form id="login-form">
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="login-email" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" id="login-password" required>
                </div>
                <button type="submit" class="btn-primary">Login</button>
                <button type="button" class="btn-secondary" onclick="navigate('public-jobs')">Browse Jobs</button>
            </form>
        </div>
    `;
    
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        try {
            console.log('Attempting login...');
            const response = await authAPI.login(email, password);
            console.log('Login response:', response);
            setToken(response.access_token);
            
            console.log('Fetching user info...');
            const user = await authAPI.getMe();
            console.log('User info:', user);
            setCurrentUser(user);
            currentUser = user;
            
            renderNavigation();
            
            // Navigate based on role
            console.log('Navigating based on role:', user.role);
            if (user.role === 'ADMIN' || user.role === 'admin') {
                navigate('admin-dashboard');
            } else if (user.role === 'RECRUITER' || user.role === 'recruiter') {
                navigate('recruiter-jobs');
            } else if (user.role === 'REVIEWER' || user.role === 'reviewer') {
                navigate('reviewer-kanban');
            } else {
                navigate('candidate-dashboard');
            }
            
            showSuccess('Login successful!');
        } catch (error) {
            showError(error.message);
        }
    });
}

function renderSetupPage() {
    const content = document.getElementById('app-content');
    content.innerHTML = `
        <div class="card" style="max-width: 500px; margin: 2rem auto;">
            <h2>Admin Setup</h2>
            <p>Create the first admin account to get started.</p>
            <form id="setup-form">
                <div class="form-group">
                    <label>First Name</label>
                    <input type="text" id="setup-firstname" required>
                </div>
                <div class="form-group">
                    <label>Last Name</label>
                    <input type="text" id="setup-lastname" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="setup-email" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" id="setup-password" required>
                </div>
                <button type="submit" class="btn-primary">Create Admin Account</button>
            </form>
        </div>
    `;
    
    document.getElementById('setup-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        try {
            const response = await authAPI.setupAdmin(
                document.getElementById('setup-email').value,
                document.getElementById('setup-password').value,
                document.getElementById('setup-firstname').value,
                document.getElementById('setup-lastname').value
            );
            
            setToken(response.access_token);
            const user = await authAPI.getMe();
            setCurrentUser(user);
            currentUser = user;
            
            renderNavigation();
            navigate('admin-dashboard');
            showSuccess('Admin account created!');
        } catch (error) {
            showError(error.message);
        }
    });
}

async function renderAdminDashboard() {
    showLoading();
    
    try {
        const [settings, users, pipelines] = await Promise.all([
            settingsAPI.get(),
            usersAPI.list(),
            pipelinesAPI.list()
        ]);
        
        const content = document.getElementById('app-content');
        content.innerHTML = `
            <h2>Admin Dashboard</h2>
            
            <div class="card">
                <h3>Branding Settings</h3>
                <form id="settings-form">
                    <div class="form-group">
                        <label>Company Name</label>
                        <input type="text" id="company-name" value="${settings.company_name || ''}" required>
                    </div>
                    <div class="form-group">
                        <label>Brand Color</label>
                        <input type="color" id="brand-color" value="${settings.brand_color || '#007bff'}">
                    </div>
                    <div class="form-group">
                        <label>Logo URL</label>
                        <input type="url" id="logo-url" value="${settings.logo_url || ''}" placeholder="https://example.com/logo.png">
                    </div>
                    <button type="submit" class="btn-primary">Save Settings</button>
                </form>
            </div>
            
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3>Users</h3>
                    <button onclick="showInviteUserModal()" class="btn-primary">Create User</button>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="users-table">
                        ${users.map(user => `
                            <tr>
                                <td>${user.first_name} ${user.last_name}</td>
                                <td>${user.email}</td>
                                <td><span class="badge badge-primary">${user.role}</span></td>
                                <td><span class="badge badge-${user.is_active ? 'success' : 'warning'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
                                <td>
                                    <button onclick="toggleUserStatus('${user.id}', ${!user.is_active})" class="btn-secondary">
                                        ${user.is_active ? 'Deactivate' : 'Activate'}
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3>Pipelines</h3>
                    <button onclick="showCreatePipelineModal()" class="btn-primary">Create Pipeline</button>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Stages</th>
                            <th>Default</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${pipelines.map(pipeline => `
                            <tr>
                                <td>${pipeline.name}</td>
                                <td>${pipeline.stages.map(s => s.name).join(' → ')}</td>
                                <td><span class="badge badge-${pipeline.is_default ? 'success' : 'secondary'}">${pipeline.is_default ? 'Yes' : 'No'}</span></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            
            <div id="modal-container"></div>
        `;
        
        document.getElementById('settings-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                await settingsAPI.update({
                    company_name: document.getElementById('company-name').value,
                    brand_color: document.getElementById('brand-color').value,
                    logo_url: document.getElementById('logo-url').value || null
                });
                showSuccess('Settings updated!');
            } catch (error) {
                showError(error.message);
            }
        });
        
    } catch (error) {
        console.error('Admin dashboard error:', error);
        const content = document.getElementById('app-content');
        content.innerHTML = `
            <div class="card">
                <h2>Error Loading Dashboard</h2>
                <p style="color: red;">${error.message}</p>
                <p>Please check the browser console for more details.</p>
                <button onclick="renderAdminDashboard()" class="btn-primary">Retry</button>
                <button onclick="navigate('login')" class="btn-secondary">Back to Login</button>
            </div>
        `;
    }
}

async function renderRecruiterJobs() {
    showLoading();
    
    try {
        const pipelines = await pipelinesAPI.list();
        currentPipelines = pipelines;
        
        const content = document.getElementById('app-content');
        content.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <h2>Jobs</h2>
                <button onclick="showCreateJobModal()" class="btn-primary">Create Job</button>
            </div>
            
            <div id="jobs-list"></div>
            <div id="modal-container"></div>
        `;
        
        loadJobsList();
        
    } catch (error) {
        showError(error.message);
    }
}

async function loadJobsList() {
    try {
        const response = await publicAPI.getJobs();
        const jobs = response.jobs;
        
        const jobsList = document.getElementById('jobs-list');
        
        if (jobs.length === 0) {
            jobsList.innerHTML = '<p>No jobs yet. Create your first job!</p>';
            return;
        }
        
        jobsList.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Department</th>
                        <th>Location</th>
                        <th>Status</th>
                        <th>Applications</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${jobs.map(job => `
                        <tr>
                            <td><strong>${job.title}</strong></td>
                            <td>${job.department || '-'}</td>
                            <td>${job.location || '-'}</td>
                            <td><span class="badge badge-${job.status === 'published' ? 'success' : job.status === 'draft' ? 'warning' : 'secondary'}">${job.status}</span></td>
                            <td>${job.application_count || 0}</td>
                            <td>
                                <button onclick="navigate('recruiter-form-builder', {jobId: '${job.id}'})" class="btn-secondary">Questions</button>
                                ${job.status === 'draft' ? 
                                    `<button onclick="updateJobStatus('${job.id}', 'published')" class="btn-primary">Publish</button>` :
                                    job.status === 'published' ?
                                    `<button onclick="updateJobStatus('${job.id}', 'closed')" class="btn-secondary">Close</button>` :
                                    ''
                                }
                                <button onclick="showJobStats('${job.id}')" class="btn-secondary">Stats</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        showError(error.message);
    }
}

function showCreateJobModal() {
    const modalContainer = document.getElementById('modal-container');
    
    if (currentPipelines.length === 0) {
        showError('Please create a pipeline first before creating a job.');
        return;
    }
    
    modalContainer.innerHTML = `
        <div class="modal active">
            <div class="modal-content" style="max-width: 600px;">
                <h3>Create Job</h3>
                <form id="job-form">
                    <div class="form-group">
                        <label>Job Title</label>
                        <input type="text" id="job-title" required>
                    </div>
                    <div class="form-group">
                        <label>Department</label>
                        <input type="text" id="job-department">
                    </div>
                    <div class="form-group">
                        <label>Location</label>
                        <input type="text" id="job-location" placeholder="Remote, New York, etc.">
                    </div>
                    <div class="form-group">
                        <label>Employment Type</label>
                        <select id="job-employment-type" required>
                            <option value="full-time">Full-time</option>
                            <option value="part-time">Part-time</option>
                            <option value="contract">Contract</option>
                            <option value="internship">Internship</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea id="job-description" rows="6" required></textarea>
                    </div>
                    <div class="form-group">
                        <label>Requirements</label>
                        <textarea id="job-requirements" rows="4" required></textarea>
                    </div>
                    <div class="form-group">
                        <label>Pipeline</label>
                        <select id="job-pipeline" required>
                            ${currentPipelines.map(p => `
                                <option value="${p.id}" ${p.is_default ? 'selected' : ''}>${p.name}</option>
                            `).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Status</label>
                        <select id="job-status" required>
                            <option value="draft">Draft</option>
                            <option value="published">Published</option>
                        </select>
                    </div>
                    <div style="display: flex; gap: 1rem;">
                        <button type="submit" class="btn-primary">Create Job</button>
                        <button type="button" onclick="closeModal()" class="btn-secondary">Cancel</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.getElementById('job-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        try {
            await jobsAPI.create({
                title: document.getElementById('job-title').value,
                department: document.getElementById('job-department').value || null,
                location: document.getElementById('job-location').value || null,
                employment_type: document.getElementById('job-employment-type').value,
                description: document.getElementById('job-description').value,
                requirements: document.getElementById('job-requirements').value,
                pipeline_id: document.getElementById('job-pipeline').value,
                status: document.getElementById('job-status').value
            });
            closeModal();
            loadJobsList();
            showSuccess('Job created successfully!');
        } catch (error) {
            showError(error.message);
        }
    });
}

async function updateJobStatus(jobId, status) {
    try {
        await jobsAPI.updateStatus(jobId, status);
        loadJobsList();
        showSuccess(`Job ${status}!`);
    } catch (error) {
        showError(error.message);
    }
}

async function showJobStats(jobId) {
    try {
        const stats = await jobsAPI.getStats(jobId);
        
        const modalContainer = document.getElementById('modal-container');
        modalContainer.innerHTML = `
            <div class="modal">
                <div class="modal-content">
                    <h3>Job Statistics</h3>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin: 1rem 0;">
                        <div class="card">
                            <h4>Total Applications</h4>
                            <p style="font-size: 2rem; font-weight: bold;">${stats.total_applications}</p>
                        </div>
                        <div class="card">
                            <h4>Average Score</h4>
                            <p style="font-size: 2rem; font-weight: bold;">${stats.average_score ? stats.average_score.toFixed(1) : 'N/A'}</p>
                        </div>
                    </div>
                    
                    <h4>Applications by Stage</h4>
                    <table>
                        <thead>
                            <tr>
                                <th>Stage</th>
                                <th>Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${Object.entries(stats.applications_by_stage).map(([stage, count]) => `
                                <tr>
                                    <td>${stage}</td>
                                    <td>${count}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                    
                    <button onclick="closeModal()" class="btn-primary" style="margin-top: 1rem;">Close</button>
                </div>
            </div>
        `;
    } catch (error) {
        showError(error.message);
    }
}

async function renderFormBuilder(params) {
    showLoading();
    
    if (!params.jobId) {
        showError('Job ID required');
        return;
    }
    
    try {
        const job = await publicAPI.getJob(params.jobId);
        
        const content = document.getElementById('app-content');
        content.innerHTML = `
            <div style="margin-bottom: 2rem;">
                <button onclick="navigate('recruiter-jobs')" class="btn-secondary">← Back to Jobs</button>
                <h2>Custom Questions for: ${job.title}</h2>
            </div>
            
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3>Application Questions</h3>
                    <button onclick="addQuestion()" class="btn-primary">Add Question</button>
                </div>
                
                <div id="questions-list">
                    ${job.custom_questions && job.custom_questions.length > 0 ? 
                        job.custom_questions.map((q, idx) => `
                            <div class="card" style="margin-bottom: 1rem; background: #f8f9fa;">
                                <div style="display: flex; justify-content: space-between;">
                                    <div style="flex: 1;">
                                        <strong>Question ${idx + 1}:</strong> ${q.question_text}
                                        <br>
                                        <small>Type: ${q.question_type} ${q.is_required ? '(Required)' : '(Optional)'}</small>
                                        ${q.options ? `<br><small>Options: ${q.options.join(', ')}</small>` : ''}
                                    </div>
                                    <button onclick="removeQuestion(${idx})" class="btn-danger">Remove</button>
                                </div>
                            </div>
                        `).join('') :
                        '<p>No custom questions yet. Add questions that candidates will answer when applying.</p>'
                    }
                </div>
                
                <button onclick="saveQuestions('${params.jobId}')" class="btn-primary" style="margin-top: 1rem;">Save Questions</button>
            </div>
            
            <div id="modal-container"></div>
        `;
        
        window.currentQuestions = job.custom_questions || [];
        
    } catch (error) {
        showError(error.message);
    }
}

function addQuestion() {
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = `
        <div class="modal">
            <div class="modal-content">
                <h3>Add Question</h3>
                <form id="question-form">
                    <div class="form-group">
                        <label>Question Text</label>
                        <textarea id="question-text" rows="3" required></textarea>
                    </div>
                    <div class="form-group">
                        <label>Question Type</label>
                        <select id="question-type" required onchange="toggleOptionsField()">
                            <option value="text">Text (Short Answer)</option>
                            <option value="textarea">Textarea (Long Answer)</option>
                            <option value="select">Multiple Choice</option>
                            <option value="multiselect">Multiple Select</option>
                        </select>
                    </div>
                    <div class="form-group" id="options-group" style="display: none;">
                        <label>Options (one per line)</label>
                        <textarea id="question-options" rows="4" placeholder="Option 1&#10;Option 2&#10;Option 3"></textarea>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="question-required" checked>
                            Required question
                        </label>
                    </div>
                    <div style="display: flex; gap: 1rem;">
                        <button type="submit" class="btn-primary">Add Question</button>
                        <button type="button" onclick="closeModal()" class="btn-secondary">Cancel</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.getElementById('question-form').addEventListener('submit', (e) => {
        e.preventDefault();
        
        const questionType = document.getElementById('question-type').value;
        const options = questionType === 'select' || questionType === 'multiselect' ?
            document.getElementById('question-options').value.split('\n').map(s => s.trim()).filter(s => s) :
            null;
        
        window.currentQuestions.push({
            question_text: document.getElementById('question-text').value,
            question_type: questionType,
            is_required: document.getElementById('question-required').checked,
            options: options
        });
        
        closeModal();
        renderFormBuilder({ jobId: new URLSearchParams(window.location.search).get('jobId') || window.currentJobId });
    });
}

function toggleOptionsField() {
    const questionType = document.getElementById('question-type').value;
    const optionsGroup = document.getElementById('options-group');
    optionsGroup.style.display = (questionType === 'select' || questionType === 'multiselect') ? 'block' : 'none';
}

function removeQuestion(index) {
    window.currentQuestions.splice(index, 1);
    renderFormBuilder({ jobId: window.currentJobId });
}

async function saveQuestions(jobId) {
    window.currentJobId = jobId;
    
    try {
        await jobsAPI.updateQuestions(jobId, window.currentQuestions);
        showSuccess('Questions saved successfully!');
        navigate('recruiter-jobs');
    } catch (error) {
        showError(error.message);
    }
}

async function renderPublicJobs() {
    showLoading();
    
    try {
        const response = await publicAPI.getJobs({ status: 'published' });
        const jobs = response.jobs;
        
        const content = document.getElementById('app-content');
        content.innerHTML = `
            <h2>Open Positions</h2>
            
            <div class="card" style="margin-bottom: 2rem;">
                <h3>Filter Jobs</h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                    <input type="text" id="filter-search" placeholder="Search title or department...">
                    <input type="text" id="filter-location" placeholder="Location...">
                    <select id="filter-employment">
                        <option value="">All Employment Types</option>
                        <option value="full-time">Full-time</option>
                        <option value="part-time">Part-time</option>
                        <option value="contract">Contract</option>
                        <option value="internship">Internship</option>
                    </select>
                </div>
                <button onclick="applyFilters()" class="btn-primary" style="margin-top: 1rem;">Apply Filters</button>
                <button onclick="clearFilters()" class="btn-secondary" style="margin-top: 1rem;">Clear Filters</button>
            </div>
            
            <div id="jobs-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1.5rem;">
                ${jobs.length === 0 ? '<p>No open positions at the moment.</p>' : 
                    jobs.map(job => `
                        <div class="card" style="cursor: pointer;" onclick="navigate('public-job-detail', {jobId: '${job.id}'})">
                            <h3>${job.title}</h3>
                            ${job.department ? `<p><strong>Department:</strong> ${job.department}</p>` : ''}
                            ${job.location ? `<p><strong>Location:</strong> ${job.location}</p>` : ''}
                            <p><span class="badge badge-primary">${job.employment_type}</span></p>
                            <p>${job.description.substring(0, 150)}...</p>
                            <button class="btn-primary" style="width: 100%;">View Details</button>
                        </div>
                    `).join('')
                }
            </div>
        `;
    } catch (error) {
        showError(error.message);
    }
}

async function applyFilters() {
    const filters = {
        status: 'published',
        search: document.getElementById('filter-search').value || undefined,
        location: document.getElementById('filter-location').value || undefined,
        employment_type: document.getElementById('filter-employment').value || undefined
    };
    
    try {
        const response = await publicAPI.getJobs(filters);
        const jobs = response.jobs;
        
        const jobsGrid = document.getElementById('jobs-grid');
        jobsGrid.innerHTML = jobs.length === 0 ? '<p>No jobs match your filters.</p>' :
            jobs.map(job => `
                <div class="card" style="cursor: pointer;" onclick="navigate('public-job-detail', {jobId: '${job.id}'})">
                    <h3>${job.title}</h3>
                    ${job.department ? `<p><strong>Department:</strong> ${job.department}</p>` : ''}
                    ${job.location ? `<p><strong>Location:</strong> ${job.location}</p>` : ''}
                    <p><span class="badge badge-primary">${job.employment_type}</span></p>
                    <p>${job.description.substring(0, 150)}...</p>
                    <button class="btn-primary" style="width: 100%;">View Details</button>
                </div>
            `).join('');
    } catch (error) {
        showError(error.message);
    }
}

function clearFilters() {
    document.getElementById('filter-search').value = '';
    document.getElementById('filter-location').value = '';
    document.getElementById('filter-employment').value = '';
    navigate('public-jobs');
}

async function renderJobDetail(params) {
    showLoading();
    
    if (!params.jobId) {
        showError('Job ID required');
        return;
    }
    
    try {
        const job = await publicAPI.getJob(params.jobId);
        
        const content = document.getElementById('app-content');
        content.innerHTML = `
            <div style="margin-bottom: 2rem;">
                <button onclick="navigate('public-jobs')" class="btn-secondary">← Back to Jobs</button>
            </div>
            
            <div class="card">
                <h1>${job.title}</h1>
                <div style="display: flex; gap: 1rem; margin: 1rem 0;">
                    ${job.department ? `<span class="badge badge-secondary">${job.department}</span>` : ''}
                    ${job.location ? `<span class="badge badge-secondary">${job.location}</span>` : ''}
                    <span class="badge badge-primary">${job.employment_type}</span>
                </div>
                
                <h3>Description</h3>
                <p style="white-space: pre-wrap;">${job.description}</p>
                
                <h3>Requirements</h3>
                <p style="white-space: pre-wrap;">${job.requirements}</p>
                
                <button onclick="navigate('public-apply', {jobId: '${job.id}'})" class="btn-primary" style="margin-top: 2rem; width: 100%; padding: 1rem; font-size: 1.1rem;">
                    Apply for this Position
                </button>
            </div>
        `;
    } catch (error) {
        showError(error.message);
    }
}

async function renderApplicationForm(params) {
    showLoading();
    
    if (!params.jobId) {
        showError('Job ID required');
        return;
    }
    
    try {
        const job = await publicAPI.getJob(params.jobId);
        
        const content = document.getElementById('app-content');
        content.innerHTML = `
            <div style="margin-bottom: 2rem;">
                <button onclick="navigate('public-job-detail', {jobId: '${job.id}'})" class="btn-secondary">← Back to Job</button>
                <h2>Apply for: ${job.title}</h2>
            </div>
            
            <div class="card">
                <form id="application-form">
                    <h3>Personal Information</h3>
                    
                    <div class="form-group">
                        <label>First Name *</label>
                        <input type="text" id="app-firstname" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Last Name *</label>
                        <input type="text" id="app-lastname" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Email *</label>
                        <input type="email" id="app-email" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="tel" id="app-phone">
                    </div>
                    
                    <div class="form-group">
                        <label>LinkedIn URL</label>
                        <input type="url" id="app-linkedin" placeholder="https://linkedin.com/in/yourprofile">
                    </div>
                    
                    <h3>Resume & Cover Letter</h3>
                    
                    <div class="form-group">
                        <label>Resume * (PDF or DOCX)</label>
                        <input type="file" id="app-resume" accept=".pdf,.docx" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Cover Letter (PDF or DOCX)</label>
                        <input type="file" id="app-cover-letter" accept=".pdf,.docx">
                    </div>
                    
                    ${job.custom_questions && job.custom_questions.length > 0 ? `
                        <h3>Additional Questions</h3>
                        ${job.custom_questions.map((q, idx) => `
                            <div class="form-group">
                                <label>${q.question_text} ${q.is_required ? '*' : ''}</label>
                                ${q.question_type === 'text' ? 
                                    `<input type="text" id="custom-q-${idx}" ${q.is_required ? 'required' : ''}>` :
                                  q.question_type === 'textarea' ?
                                    `<textarea id="custom-q-${idx}" rows="4" ${q.is_required ? 'required' : ''}></textarea>` :
                                  q.question_type === 'select' ?
                                    `<select id="custom-q-${idx}" ${q.is_required ? 'required' : ''}>
                                        <option value="">Select an option...</option>
                                        ${q.options.map(opt => `<option value="${opt}">${opt}</option>`).join('')}
                                    </select>` :
                                  q.question_type === 'multiselect' ?
                                    `<select id="custom-q-${idx}" multiple ${q.is_required ? 'required' : ''}>
                                        ${q.options.map(opt => `<option value="${opt}">${opt}</option>`).join('')}
                                    </select>` :
                                    ''
                                }
                            </div>
                        `).join('')}
                    ` : ''}
                    
                    <button type="submit" class="btn-primary" style="width: 100%; padding: 1rem; font-size: 1.1rem;">
                        Submit Application
                    </button>
                </form>
            </div>
        `;
        
        document.getElementById('application-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData();
            formData.append('first_name', document.getElementById('app-firstname').value);
            formData.append('last_name', document.getElementById('app-lastname').value);
            formData.append('email', document.getElementById('app-email').value);
            formData.append('phone', document.getElementById('app-phone').value || '');
            formData.append('linkedin_url', document.getElementById('app-linkedin').value || '');
            
            const resumeFile = document.getElementById('app-resume').files[0];
            if (resumeFile) {
                formData.append('resume', resumeFile);
            }
            
            const coverLetterFile = document.getElementById('app-cover-letter').files[0];
            if (coverLetterFile) {
                formData.append('cover_letter', coverLetterFile);
            }
            
            // Add custom question answers
            if (job.custom_questions && job.custom_questions.length > 0) {
                const answers = job.custom_questions.map((q, idx) => {
                    const element = document.getElementById(`custom-q-${idx}`);
                    let answer_value;
                    
                    if (q.question_type === 'multiselect') {
                        const selected = Array.from(element.selectedOptions).map(opt => opt.value);
                        answer_value = selected.join(', ');
                    } else {
                        answer_value = element.value;
                    }
                    
                    return {
                        question_text: q.question_text,
                        answer_value: answer_value
                    };
                });
                
                formData.append('custom_answers', JSON.stringify(answers));
            }
            
            try {
                showLoading();
                await publicAPI.apply(job.id, formData);
                
                const content = document.getElementById('app-content');
                content.innerHTML = `
                    <div class="card" style="text-align: center; padding: 3rem;">
                        <h2>Application Submitted!</h2>
                        <p style="font-size: 1.2rem; margin: 2rem 0;">Thank you for applying to ${job.title}.</p>
                        <p>We'll review your application and get back to you soon.</p>
                        <button onclick="navigate('public-jobs')" class="btn-primary" style="margin-top: 2rem;">Browse More Jobs</button>
                    </div>
                `;
            } catch (error) {
                showError(error.message);
            }
        });
        
    } catch (error) {
        showError(error.message);
    }
}

async function renderKanbanBoard() {
    showLoading();
    
    try {
        const jobs = await publicAPI.getJobs({ status: 'published' });
        
        const content = document.getElementById('app-content');
        content.innerHTML = `
            <h2>Applications</h2>
            
            <div class="card" style="margin-bottom: 2rem;">
                <h3>Filter Applications</h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                    <select id="filter-job" onchange="loadApplications()">
                        <option value="">All Jobs</option>
                        ${jobs.jobs.map(job => `<option value="${job.id}">${job.title}</option>`).join('')}
                    </select>
                    <select id="filter-score" onchange="loadApplications()">
                        <option value="">All Scores</option>
                        <option value="80">80+ (Excellent)</option>
                        <option value="60">60+ (Good)</option>
                        <option value="40">40+ (Fair)</option>
                    </select>
                    <input type="text" id="filter-candidate" placeholder="Candidate name..." onchange="loadApplications()">
                </div>
            </div>
            
            <div id="kanban-container"></div>
        `;
        
        loadApplications();
        
    } catch (error) {
        showError(error.message);
    }
}

async function loadApplications() {
    try {
        const filters = {
            job_id: document.getElementById('filter-job')?.value || undefined,
            min_score: document.getElementById('filter-score')?.value || undefined,
            search: document.getElementById('filter-candidate')?.value || undefined
        };
        
        const response = await applicationsAPI.list(filters);
        const applications = response.applications;
        
        // Group by stage
        const stages = {};
        applications.forEach(app => {
            const stageName = app.current_stage?.name || 'Unassigned';
            if (!stages[stageName]) {
                stages[stageName] = [];
            }
            stages[stageName].push(app);
        });
        
        const kanbanContainer = document.getElementById('kanban-container');
        kanbanContainer.innerHTML = `
            <div class="kanban-board">
                ${Object.entries(stages).map(([stageName, apps]) => `
                    <div class="kanban-column">
                        <h3>${stageName} <span class="badge badge-secondary">${apps.length}</span></h3>
                        ${apps.map(app => `
                            <div class="kanban-card" onclick="navigate('reviewer-application', {applicationId: '${app.id}'})">
                                <h4>${app.candidate_name}</h4>
                                <p>${app.job_title}</p>
                                ${app.ai_insights?.overall_score ? 
                                    `<span class="badge badge-${app.ai_insights.overall_score >= 80 ? 'success' : app.ai_insights.overall_score >= 60 ? 'primary' : 'warning'}">
                                        Score: ${app.ai_insights.overall_score}
                                    </span>` : 
                                    '<span class="badge badge-secondary">Pending AI</span>'
                                }
                                <small style="display: block; margin-top: 0.5rem;">Applied: ${new Date(app.applied_at).toLocaleDateString()}</small>
                            </div>
                        `).join('')}
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        showError(error.message);
    }
}

async function renderApplicationDetail(params) {
    showLoading();
    
    if (!params.applicationId) {
        showError('Application ID required');
        return;
    }
    
    try {
        const app = await applicationsAPI.get(params.applicationId);
        
        const content = document.getElementById('app-content');
        content.innerHTML = `
            <div style="margin-bottom: 2rem;">
                <button onclick="navigate('reviewer-kanban')" class="btn-secondary">← Back to Board</button>
                <h2>${app.candidate_name}</h2>
            </div>
            
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem;">
                <div>
                    <div class="card">
                        <h3>Candidate Information</h3>
                        <p><strong>Job:</strong> ${app.job_title}</p>
                        <p><strong>Email:</strong> ${app.candidate_email}</p>
                        ${app.phone ? `<p><strong>Phone:</strong> ${app.phone}</p>` : ''}
                        ${app.linkedin_url ? `<p><strong>LinkedIn:</strong> <a href="${app.linkedin_url}" target="_blank">${app.linkedin_url}</a></p>` : ''}
                        <p><strong>Applied:</strong> ${new Date(app.applied_at).toLocaleString()}</p>
                        <p><strong>Current Stage:</strong> <span class="badge badge-primary">${app.current_stage?.name || 'Unassigned'}</span></p>
                    </div>
                    
                    ${app.attachments && app.attachments.length > 0 ? `
                        <div class="card">
                            <h3>Attachments</h3>
                            ${app.attachments.map(att => `
                                <p>📄 ${att.file_type === 'resume' ? '📋 Resume' : '📝 Cover Letter'}: ${att.file_path.split('/').pop()}</p>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    ${app.custom_answers && app.custom_answers.length > 0 ? `
                        <div class="card">
                            <h3>Application Answers</h3>
                            ${app.custom_answers.map(ans => `
                                <div style="margin-bottom: 1rem;">
                                    <strong>${ans.question_text}</strong>
                                    <p>${ans.answer_value}</p>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    <div class="card">
                        <h3>Comments</h3>
                        <div id="comments-list">
                            ${app.comments && app.comments.length > 0 ?
                                app.comments.map(comment => `
                                    <div class="card" style="background: #f8f9fa; margin-bottom: 1rem;">
                                        <strong>${comment.author_name}</strong>
                                        <small style="color: #666;">${new Date(comment.created_at).toLocaleString()}</small>
                                        <p style="margin-top: 0.5rem;">${comment.content}</p>
                                    </div>
                                `).join('') :
                                '<p>No comments yet.</p>'
                            }
                        </div>
                        
                        <form id="comment-form" style="margin-top: 1rem;">
                            <div class="form-group">
                                <textarea id="comment-text" rows="3" placeholder="Add a comment..." required></textarea>
                            </div>
                            <button type="submit" class="btn-primary">Add Comment</button>
                        </form>
                    </div>
                </div>
                
                <div>
                    ${app.ai_insights ? `
                        <div class="card">
                            <h3>AI Insights</h3>
                            <div style="text-align: center; margin: 1rem 0;">
                                <h1 style="font-size: 3rem; color: ${app.ai_insights.overall_score >= 80 ? '#28a745' : app.ai_insights.overall_score >= 60 ? '#007bff' : '#ffc107'};">
                                    ${app.ai_insights.overall_score}
                                </h1>
                                <p>Overall Score</p>
                            </div>
                            
                            ${app.ai_insights.strengths ? `
                                <h4>Strengths</h4>
                                <ul>
                                    ${app.ai_insights.strengths.map(s => `<li>${s}</li>`).join('')}
                                </ul>
                            ` : ''}
                            
                            ${app.ai_insights.weaknesses ? `
                                <h4>Weaknesses</h4>
                                <ul>
                                    ${app.ai_insights.weaknesses.map(w => `<li>${w}</li>`).join('')}
                                </ul>
                            ` : ''}
                            
                            ${app.ai_insights.summary ? `
                                <h4>Summary</h4>
                                <p>${app.ai_insights.summary}</p>
                            ` : ''}
                            
                            <button onclick="reanalyzeApplication('${app.id}')" class="btn-secondary" style="width: 100%; margin-top: 1rem;">
                                🔄 Re-analyze
                            </button>
                        </div>
                    ` : `
                        <div class="card">
                            <h3>AI Insights</h3>
                            <p>AI analysis pending...</p>
                            <button onclick="reanalyzeApplication('${app.id}')" class="btn-primary" style="width: 100%;">
                                Analyze Now
                            </button>
                        </div>
                    `}
                    
                    <div class="card">
                        <h3>Actions</h3>
                        
                        <h4>Vote</h4>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; margin-bottom: 1rem;">
                            <button onclick="vote('${app.id}', 1)" class="btn-primary">👍 Yes</button>
                            <button onclick="vote('${app.id}', 0)" class="btn-secondary">🤔 Maybe</button>
                            <button onclick="vote('${app.id}', -1)" class="btn-danger">👎 No</button>
                        </div>
                        
                        <h4>Move to Stage</h4>
                        <select id="stage-select" class="form-group">
                            ${app.pipeline_stages?.map(stage => `
                                <option value="${stage.id}" ${stage.id === app.current_stage?.id ? 'selected' : ''}>
                                    ${stage.name}
                                </option>
                            `).join('')}
                        </select>
                        <button onclick="moveStage('${app.id}')" class="btn-primary" style="width: 100%;">Move</button>
                    </div>
                    
                    ${app.activities && app.activities.length > 0 ? `
                        <div class="card">
                            <h3>Activity Log</h3>
                            ${app.activities.map(activity => `
                                <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #dee2e6;">
                                    <strong>${activity.activity_type}</strong>
                                    <small style="display: block; color: #666;">${new Date(activity.created_at).toLocaleString()}</small>
                                    ${activity.metadata ? `<p style="margin-top: 0.5rem; font-size: 0.9rem;">${JSON.stringify(activity.metadata)}</p>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        document.getElementById('comment-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                await applicationsAPI.comment(app.id, document.getElementById('comment-text').value);
                navigate('reviewer-application', { applicationId: app.id });
                showSuccess('Comment added!');
            } catch (error) {
                showError(error.message);
            }
        });
        
    } catch (error) {
        showError(error.message);
    }
}

async function vote(applicationId, voteValue) {
    try {
        await applicationsAPI.vote(applicationId, voteValue);
        showSuccess('Vote recorded!');
        navigate('reviewer-application', { applicationId });
    } catch (error) {
        showError(error.message);
    }
}

async function moveStage(applicationId) {
    const stageId = document.getElementById('stage-select').value;
    
    try {
        await applicationsAPI.moveStage(applicationId, stageId);
        showSuccess('Application moved!');
        navigate('reviewer-application', { applicationId });
    } catch (error) {
        showError(error.message);
    }
}

async function reanalyzeApplication(applicationId) {
    try {
        await applicationsAPI.reanalyze(applicationId);
        showSuccess('Re-analysis triggered! Refresh in a moment to see updated insights.');
    } catch (error) {
        showError(error.message);
    }
}

async function renderCandidateDashboard() {
    showLoading();
    
    try {
        // Get applications for current candidate
        const response = await applicationsAPI.list({ candidate_email: currentUser.email });
        const applications = response.applications;
        
        const content = document.getElementById('app-content');
        content.innerHTML = `
            <h2>My Applications</h2>
            
            ${applications.length === 0 ? `
                <div class="card" style="text-align: center; padding: 3rem;">
                    <h3>No applications yet</h3>
                    <p>Browse open positions and apply to get started!</p>
                    <button onclick="navigate('public-jobs')" class="btn-primary" style="margin-top: 1rem;">Browse Jobs</button>
                </div>
            ` : `
                <div class="card">
                    <table>
                        <thead>
                            <tr>
                                <th>Job Title</th>
                                <th>Applied Date</th>
                                <th>Current Stage</th>
                                <th>Status</th>
                                <th>AI Score</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${applications.map(app => `
                                <tr>
                                    <td><strong>${app.job_title}</strong></td>
                                    <td>${new Date(app.applied_at).toLocaleDateString()}</td>
                                    <td><span class="badge badge-primary">${app.current_stage?.name || 'Under Review'}</span></td>
                                    <td><span class="badge badge-success">Active</span></td>
                                    <td>
                                        ${app.ai_insights?.overall_score ? 
                                            `<span class="badge badge-${app.ai_insights.overall_score >= 80 ? 'success' : app.ai_insights.overall_score >= 60 ? 'primary' : 'warning'}">
                                                ${app.ai_insights.overall_score}
                                            </span>` :
                                            '<span class="badge badge-secondary">Pending</span>'
                                        }
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                
                <div style="margin-top: 2rem;">
                    <button onclick="navigate('public-jobs')" class="btn-primary">Apply to More Jobs</button>
                </div>
            `}
        `;
    } catch (error) {
        showError(error.message);
    }
}

// Admin Modal Functions
function showInviteUserModal() {
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = `
        <div class="modal active">
            <div class="modal-content">
                <h3>Create User Account</h3>
                <form id="invite-form">
                    <div class="form-group">
                        <label>First Name</label>
                        <input type="text" id="invite-firstname" required>
                    </div>
                    <div class="form-group">
                        <label>Last Name</label>
                        <input type="text" id="invite-lastname" required>
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="invite-email" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" id="invite-password" required minlength="8" placeholder="Minimum 8 characters">
                    </div>
                    <div class="form-group">
                        <label>Role</label>
                        <select id="invite-role" required>
                            <option value="ADMIN">Admin</option>
                            <option value="RECRUITER">Recruiter</option>
                            <option value="REVIEWER">Reviewer</option>
                        </select>
                    </div>
                    <div style="display: flex; gap: 1rem;">
                        <button type="submit" class="btn-primary">Create User</button>
                        <button type="button" onclick="closeModal()" class="btn-secondary">Cancel</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.getElementById('invite-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        try {
            await usersAPI.create(
                document.getElementById('invite-email').value,
                document.getElementById('invite-password').value,
                document.getElementById('invite-role').value,
                document.getElementById('invite-firstname').value,
                document.getElementById('invite-lastname').value
            );
            closeModal();
            navigate('admin-dashboard');
            showSuccess('User account created successfully!');
        } catch (error) {
            showError(error.message);
        }
    });
}

function showCreatePipelineModal() {
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = `
        <div class="modal active">
            <div class="modal-content">
                <h3>Create Pipeline</h3>
                <form id="pipeline-form">
                    <div class="form-group">
                        <label>Pipeline Name</label>
                        <input type="text" id="pipeline-name" required placeholder="e.g., Standard Hiring Process">
                    </div>
                    <div class="form-group">
                        <label>Stages (comma-separated)</label>
                        <input type="text" id="pipeline-stages" required placeholder="e.g., Applied, Screening, Interview, Offer">
                        <small>Enter stage names separated by commas</small>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="pipeline-default">
                            Set as default pipeline
                        </label>
                    </div>
                    <div style="display: flex; gap: 1rem;">
                        <button type="submit" class="btn-primary">Create Pipeline</button>
                        <button type="button" onclick="closeModal()" class="btn-secondary">Cancel</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.getElementById('pipeline-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        try {
            const name = document.getElementById('pipeline-name').value;
            const stagesInput = document.getElementById('pipeline-stages').value;
            const isDefault = document.getElementById('pipeline-default').checked;
            
            // Parse stages - just get the names as an array
            const stages = stagesInput.split(',').map(s => s.trim()).filter(s => s.length > 0);
            
            await pipelinesAPI.create(name, stages, isDefault);
            closeModal();
            navigate('admin-dashboard');
            showSuccess('Pipeline created successfully!');
        } catch (error) {
            showError(error.message);
        }
    });
}

function closeModal() {
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = '';
}

async function toggleUserStatus(userId, isActive) {
    try {
        await usersAPI.update(userId, { is_active: isActive });
        navigate('admin-dashboard');
        showSuccess(`User ${isActive ? 'activated' : 'deactivated'} successfully!`);
    } catch (error) {
        showError(error.message);
    }
}

function closeModal() {
    document.getElementById('modal-container').innerHTML = '';
}

// Initialize App
async function init() {
    renderNavigation();
    
    // Check if setup is needed
    try {
        await authAPI.getMe();
        // If token valid, navigate based on role
        if (currentUser) {
            if (currentUser.role === 'ADMIN' || currentUser.role === 'admin') {
                navigate('admin-dashboard');
            } else if (currentUser.role === 'RECRUITER' || currentUser.role === 'recruiter') {
                navigate('recruiter-jobs');
            } else if (currentUser.role === 'REVIEWER' || currentUser.role === 'reviewer') {
                navigate('reviewer-kanban');
            } else {
                navigate('candidate-dashboard');
            }
        } else {
            navigate('login');
        }
    } catch (error) {
        // Check if setup needed
        if (error.message.includes('setup') || error.message.includes('No users')) {
            navigate('setup');
        } else {
            navigate('login');
        }
    }
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
