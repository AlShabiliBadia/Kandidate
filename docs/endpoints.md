## Authentication & Users

| **Method** | **Endpoint**           | **Description**                                                            |
| ---------- | ---------------------- | -------------------------------------------------------------------------- |
| **POST**   | `/auth/login`          | Standard login (returns JWT Token).                                        |
| **POST**   | `/auth/setup-admin`    | **First run only.** Sets the initial Admin email/password.                 |
| **POST**   | `/auth/set-password`   | Used by **Guests** (candidates) to activate their account via email token. |
| **POST**   | `/auth/reset-password` | Standard "Forgot Password" flow.                                           |
| **GET**    | `/users/me`            | Get current logged-in user details.                                        |
| **GET**    | `/users`               | List all team members (Recruiters/Reviewers).                              |
| **POST**   | `/users/invite`        | Admin invites a new team member (sends email).                             |
| **PATCH**  | `/users/{id}`          | Update role or deactivate a user.                                          |

## System Configuration

| **Method** | **Endpoint** | **Description**                                            |
| ---------- | ------------ | ---------------------------------------------------------- |
| **GET**    | `/settings`  | Get logo, brand color, company name (Publicly accessible). |
| **PUT**    | `/settings`  | Admin updates branding/config.                             |
| **GET**    | `/pipelines` | Get the hiring pipelines (e.g., "Engineering Flow").       |
| **POST**   | `/pipelines` | Create a new custom pipeline structure.                    |

## Job Management

| **Method** | **Endpoint**                | **Description**                                                   |
| ---------- | --------------------------- | ----------------------------------------------------------------- |
| **POST**   | `/jobs`                     | Create a new Job Draft.                                           |
| **PUT**    | `/jobs/{id}`                | Update Job details (Title, Salary, Description).                  |
| **PATCH**  | `/jobs/{id}/status`         | Publish or Close a job.                                           |
| **PUT**    | `/jobs/{id}/questions`      | **Form Builder:** Save the list of custom questions for this job. |
| **POST**   | `/jobs/{id}/tracking-links` | Generate a "Source Link" (e.g., for LinkedIn).                    |
| **GET**    | `/jobs/{id}/stats`          | Get basic analytics (View count, Application count).              |

## Public Job Board

| **Method** | **Endpoint**          | **Description**                                                       |
| ---------- | --------------------- | --------------------------------------------------------------------- |
| **GET**    | `/public/jobs`        | List all `PUBLISHED` jobs. Supports filters (`?dept=Eng&loc=Remote`). |
| **GET**    | `/public/jobs/{slug}` | Get details of a specific job + **Its Custom Questions**.             |

## Candidate Application

| **Method** | **Endpoint**              | **Description**                                                                                                                                                                                                                                                                                                                                      |
| ---------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **POST**   | `/public/jobs/{id}/apply` | **The Mega Endpoint.**<br><br> <br><br>1. Receives `Multipart/Form-Data` (Resume file + JSON fields).<br><br> <br><br>2. Uploads file to Storage (S3/Local).<br><br> <br><br>3. **Creates Shadow User** if email is new.<br><br> <br><br>4. **Saves Snapshot** to `applications` table.<br><br> <br><br>5. **Triggers AI Analysis** background task. |

## Recruitment Workspace

| **Method** | **Endpoint**                    | **Description**                                                                                                                                                                                                                |
| ---------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **GET**    | `/applications`                 | **The Kanban Feed.**<br><br> <br><br>Supports complex filters:<br><br> <br><br>`?job_id=123`<br><br> <br><br>`?stage=interview`<br><br> <br><br>`?sort=match_score_desc`<br><br> <br><br>`?q_visa=yes` (Custom Answer Filter). |
| **GET**    | `/applications/{id}`            | Get full application details (Snapshot + AI Analysis + File Links).                                                                                                                                                            |
| **PATCH**  | `/applications/{id}/stage`      | **Move Candidate:** Updates `current_stage_id`. Logs activity.                                                                                                                                                                 |
| **POST**   | `/applications/{id}/vote`       | Reviewer casts `+1` or `-1`.                                                                                                                                                                                                   |
| **POST**   | `/applications/{id}/comment`    | Add internal note.                                                                                                                                                                                                             |
| **POST**   | `/applications/{id}/re-analyze` | Manually re-trigger the AI analysis (if needed).                                                                                                                                                                               |

## Candidate Dashboard

| **Method** | **Endpoint**              | **Description**                                                |
| ---------- | ------------------------- | -------------------------------------------------------------- |
| **GET**    | `/candidate/applications` | List my applications and their current status.                 |
| **PUT**    | `/candidate/profile`      | Update my "Global" profile (only affects future applications). |
