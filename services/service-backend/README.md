# Service: API Gateway

The API Gateway acts as the single entry point for the frontend. It orchestrates the flow between the user, the file system, the message queue, and the database services. It does not perform heavy processing; it offloads work asynchronously.

## Tech Stack

- **Web Framework:** FastAPI
- **Database (Cold Storage):** PostgreSQL + SQLAlchemy (async), MongoDB (via Results Service)
- **Messaging:** Pika (RabbitMQ)
- **File Storage:** Docker Shared Volume
- **Validation:** Pydantic

## Key Architectural Flows

### 1. Asynchronous Job Submission (POST /jobs/submit)

This endpoint implements the "Fire and Forget" pattern to ensure high responsiveness.

- **Validation**: Accepts multipart/form-data (PDF/DOCX). Rejects empty payloads immediately (400).
- **Persistence (Disk)**: Saves raw files to a Docker Shared Volume so the Parser Service can access them later.
- **Persistence (Hot DB)**: Creates an initial "Pending" job record in MongoDB via the Results Service.
  - **Rollback**: If MongoDB fails, files are deleted from disk to prevent orphans.
- **Queueing**: Publishes a message to RabbitMQ (jobs_queue) to trigger the pipeline.
  - **Rollback**: If RabbitMQ fails, both MongoDB record and files are deleted.
- **Response**: Returns 202 Accepted with a job_id. The client must poll for status.

### 2. The "Sync" / ETL Process (POST /jobs/{id}/sync)

This endpoint triggers the migration of data from "Hot Storage" (MongoDB) to "Cold Storage" (PostgreSQL).

- **Check**: Verifies the job status in MongoDB is complete.
- **Incremental Sync**: Checks if the Job ID already exists in PostgreSQL.
  - **If Exists**: Adds only new CVs (deduplication logic) and updates totals.
  - **If New**: Creates the Job record and inserts all CVs.
- **Cleanup**: Upon successful sync, deletes the raw data from MongoDB to save space and maintain a single source of truth.

## API Reference

### 1. Submit Job

**Endpoint**: `POST /jobs/submit`  
**Content-Type**: `multipart/form-data`

**Parameters**:

- `files`: List of files (PDF/DOCX)
- `jd_text`: String (Job Description)
- `use_delay`: Boolean (Default: true - enforces rate limiting for Free Tier AI)

**Response (202 Accepted)**:

```json
{
  "job_id": "550e8400-e29b",
  "correlation_id": "abc-123",
  "status": "queued",
  "file_count": 3,
  "cv_details": [
    { "cv_id": "550e8400_000", "original_filename": "resume1.pdf" }
  ]
}
```

### 2. Check Status

**Endpoint**: `GET /jobs/{job_id}/status`

**Response**: Proxies the full job document from the Results Service (MongoDB).

```json
{
  "_id": "550e8400-e29b",
  "correlation_id": "abc-123",
  "jd_text": "We are looking for...",
  "status": "pending",
  "expected_files": 3,
  "results": [
    {
      "cv_id": "550e8400_000",
      "candidate_name": "John Doe",
      "match_score": 85,
      "recommendation": "Strong Hire"
    }
  ],
  "errors": [],
  "created_at": "2025-11-17T10:30:00.000000"
}
```

**Note**: `status` can be "pending" or "complete". Track progress by comparing `len(results) + len(errors)` against `expected_files`.

### 3. Final Results (PostgreSQL)

**Endpoint**: `GET /jobs/{job_id}/results`

**Response**: Returns the structured analysis from PostgreSQL (only successful CVs).

```json
{
  "job_id": "550e8400-e29b",
  "correlation_id": "abc-123",
  "jd_text": "We are looking for...",
  "total_successful_cvs": 3,
  "analyses": [
    {
      "cv_id": "550e8400_000",
      "candidate_name": "John Doe",
      "match_score": 85,
      "email": "john@example.com",
      "phone": "+1234567890",
      "skills": ["Python", "FastAPI", "Docker"],
      "experience_years": 5,
      "education": "Bachelor's in Computer Science",
      "recommendation": "Strong Hire",
      "key_strengths": ["Strong backend experience", "Cloud native"],
      "concerns": []
    }
  ]
}
```
