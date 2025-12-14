## 1. Global Definitions & Roles

**Access Control (RBAC):** The system must distinguish between the following roles.

1. **Admin:** Full access to system configuration, instance settings, and user management.
2. **Recruiter/Hiring Manager:** Can create jobs, manage pipelines, and interact with candidates.
3. **Reviewer/Interviewer:** Can view assigned candidates and leave feedback/votes (cannot edit job details or salaries).
4. **Guest/Candidate:** External users applying for jobs.

---

## 2. Role: Company Admin

_The user responsible for the initial setup and maintenance of the company instance._

### 2.1 First-Time Setup (Onboarding)

- **Default Login:** Upon first deployment, the system must generate/accept default credentials (e.g., via ENV variables or initial registration).
- **Forced Update:** On the very first login, the Admin **MUST** be redirected to a profile update page to:
  - Verify/Change Email Address.
  - Set a secure Password.
  - (Optional) Set First/Last Name.
- **System Action:** The account is not considered "Active" until this step is completed.

### 2.2 Organization Management

- **Branding:** Admin can update:
  - Company Name.
  - Company Website URL.
  - Logo (Image Upload).
  - Primary Brand Color (Hex Code) - _for the career page theme._
- **User Management:**
  - **Invite Users:** Admin can invite team members via email and assign them a role (Recruiter or Reviewer).
  - **Deactivate Users:** Admin can revoke access for a user (soft delete) without deleting their historical data (comments/votes).

### 2.3 Pipeline Configuration

- **Default Pipeline:** System provides a standard workflow: `Applied` -> `Screening` -> `Interview` -> `Offer` -> `Hired` -> `Rejected`.
- **Custom Pipelines:** Admin can create named pipelines (e.g., "Engineering Flow") and define custom stages (e.g., adding a "Take-home Test" stage).

---

## 3. Role: Recruiter / Hiring Manager

_The primary operator of the platform._

### 3.1 Job Management

- **Create/Edit Job:**
  - **Basic Info:** Title, Description (Rich Text).
  - **Structured Data (For Filtering):**
    - Department (e.g., Engineering, Sales).
    - Job Type (Full-time, Contract, Internship).
    - Workplace Type (Remote, On-site, Hybrid).
    - Location (City/Country).
    - Salary Range (Min/Max) + Currency.
  - **Pipeline Selection:** Choose which hiring pipeline applies to this job.
  - **Status:** Draft (hidden), Published (visible), Closed (archived).

### 3.2 The Form Builder (Job Specific)

- The Recruiter can define a custom application form for each job.
- **Input Types Supported:**
  - `Short Text` (e.g., "LinkedIn URL").
  - `Long Text` (e.g., "Why do you want to join us?").
  - `Yes/No` (e.g., "Do you require a visa sponsor?").
  - `Select/Dropdown` (e.g., "Years of experience: 1, 2, 3+").
  - `File Upload` (e.g., "Portfolio PDF").
- **Constraints:** Toggle `Is Required?` for each question.

### 3.3 Tracking & Sharing

- **Generate Link:** Recruiter selects a job and inputs a "Source Name" (e.g., "LinkedIn", "Twitter").
- **System Action:** Generates a unique URL (e.g., `.../jobs/101?source=linkedin`).
- **Purpose:** Applicants using this link will have their application tagged with this source automatically.

---

## 4. Role: Guest / Candidate

_The external user flow. Prioritizes low friction._

### 4.1 Discovery

- **View Job Board:** View list of all "Published" jobs.
- **Filtering:** Filter jobs by Department, Remote/On-site, and Job Type.
- **Job Details:** Click a job to view full description and salary range.

### 4.2 Application Process (The "Shadow Account" Flow)

- **Step 1: Personal Info:** Input First Name, Last Name, Email, Phone.
- **Step 2: Attachments:** Upload Resume (PDF/DOCX) and Cover Letter.
- **Step 3: Screening:** Answer the custom questions defined in the Form Builder (3.2).
- **Step 4: Submission & Snapshot:**
  - **Snapshot Creation:** The system saves the Candidate's Name, Email, Phone, Links, and Resume **specifically to this Application record**. (This ensures that if the user changes their profile later, this application remains historically accurate).
  - **User Check:**
    - If email **does not** exist -> Create "Shadow User" (Guest).
    - If email **does** exist -> Associate Application with User ID.
- **Step 5: Automated Screening (Backend Job):**
  - **AI Trigger:** System immediately sends the **Resume + Cover Letter** (but NOT the Form Answers) to the AI Engine.
  - **Output Generation:** AI generates a `Match Score`, `Risk Assessment`, and `Qualitative Analysis` to be stored in the database.

### 4.3 Post-Application Logic

- **Email Trigger:** System sends an email to the candidate.
  - _Content:_ "Application Received. To track status, set your password here: [Link]."
- **Account Activation:** If the user clicks the link and sets a password, their status updates from "Guest" to "Active User."
- **User Dashboard:** Once logged in, the user can see a table of their applications: `Job Title` | `Date Applied` | `Current Status`.

---

## 5. Role: Reviewer / Interviewer

_The internal user evaluating candidates._

### **5.1 Candidate Management (Kanban/List)**

- **View Candidates:** See applicants grouped by Pipeline Stage.
- **Smart Filtering (The Hybrid Model):**
  - **Hard Filters:** Reviewer can filter the list using the **Custom Form Answers** (e.g., "Show only candidates who answered 'Yes' to Visa").
  - **Sorting:** Reviewer can sort candidates by **AI Match Score** (High to Low).
- **Move Candidates:** Drag and drop... (Rest remains the same)

### **5.2 Application Review**

- **Candidate Profile:** View the **Snapshot Details** (Name/Phone/Links applied with).
- **AI Insights Panel:**
  - View the **Match Score** (0-100).
  - View **Risk Flags** (e.g., "Short Tenure").
  - View **AI Summary** and **Skill Gaps**.
- **File Viewer:** View Resume... (Rest remains the same)
- **Custom Answers:** View responses to Form Builder questions.

### 5.3 Feedback System (Simple)

- **Voting:**
  - Action: Upvote (+1) or Downvote (-1).
  - Visibility: Aggregated score shown on candidate card.
- **Comments:**
  - Action: Leave a text comment on the candidate's application.
  - Context: Comments are internal-only (never visible to candidate).
