# Kandidate Frontend - Testing Interface

Simple vanilla HTML/CSS/JavaScript frontend for testing all Kandidate API endpoints.

## Setup

1. **Ensure backend is running:**

   ```bash
   cd /Users/badiea/Desktop/Github/kandidate
   docker-compose up
   ```

2. **Open the frontend:**
   - Simply open `index.html` in your browser
   - Or use a simple HTTP server:
     ```bash
     cd frontend
     python3 -m http.server 3000
     # Then visit http://localhost:3000
     ```

## First-Time Setup

**Admin Credentials (Already Created):**

- Email: `admin@kandidate.com`
- Password: `admin123`

1. **Login:**

   - Open the frontend and login with the credentials above

2. **Create Pipeline:**

   - From Admin Dashboard, create a default pipeline
   - Example stages: Applied → Phone Screen → Technical Interview → Final Interview → Offer → Hired

3. **Invite Users:**
   - Admin: Full system access
   - Recruiter: Can create jobs, manage questions
   - Reviewer: Can review applications, vote, comment

## Testing Workflow

### As Admin (Full Access)

- **Admin Dashboard** → Branding settings, user management, pipeline configuration
- Access to all recruiter and reviewer features

### As Recruiter

1. **Jobs Page** → Create new job posting
2. **Form Builder** → Add custom application questions
3. **Publish Job** → Make job visible on public board
4. **Job Stats** → View application counts and metrics

### As Public Candidate

1. **Browse Jobs** → Search and filter open positions
2. **View Job Detail** → Read full description
3. **Apply** → Upload resume + cover letter, answer custom questions
4. **Track Applications** → View status in candidate dashboard (after creating account)

### As Reviewer

1. **Kanban Board** → View applications grouped by pipeline stage
2. **Application Detail** →
   - View candidate info, resume, answers
   - See AI insights (score, strengths, weaknesses)
   - Vote (Yes/Maybe/No)
   - Add comments
   - Move to different stages
   - Trigger re-analysis

## API Endpoints Covered

### Authentication

- `POST /auth/setup-admin` - First-time setup
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Settings

- `GET /settings` - Get branding settings
- `PUT /settings` - Update branding

### Users

- `GET /users` - List all users
- `POST /users/invite` - Invite new user
- `PATCH /users/{id}` - Update user status

### Pipelines

- `GET /pipelines` - List pipelines
- `POST /pipelines` - Create pipeline

### Jobs

- `GET /jobs` - List all jobs (recruiter view)
- `POST /jobs` - Create job
- `PATCH /jobs/{id}/status` - Publish/close job
- `PUT /jobs/{id}/questions` - Update custom questions
- `GET /jobs/{id}/stats` - Job statistics

### Public

- `GET /public/jobs` - Public job board (with filters)
- `GET /public/jobs/{id}` - Job details
- `POST /public/jobs/{id}/apply` - Submit application (multipart/form-data)

### Applications

- `GET /applications` - List applications (with filters)
- `GET /applications/{id}` - Application detail
- `PATCH /applications/{id}/stage` - Move to different stage
- `POST /applications/{id}/vote` - Record vote
- `POST /applications/{id}/comment` - Add comment
- `POST /applications/{id}/re-analyze` - Trigger AI re-analysis

## Features

- ✅ Role-based navigation and permissions
- ✅ JWT token authentication with localStorage
- ✅ File upload support (resume + cover letter)
- ✅ Dynamic form generation for custom questions
- ✅ Real-time filters on jobs and applications
- ✅ Modal dialogs for create/edit actions
- ✅ Success/error message toasts
- ✅ Loading states
- ✅ No frameworks required - pure vanilla JS

## Tech Stack

- **No frameworks** - Vanilla HTML/CSS/JavaScript
- **localStorage** - Token and user persistence
- **Fetch API** - All HTTP requests
- **CSS Grid/Flexbox** - Responsive layouts

## Notes

- Backend must be running on `http://localhost:8000`
- CORS is enabled on backend for local development
- File uploads use `multipart/form-data`
- All dates formatted with `toLocaleDateString()` / `toLocaleString()`
