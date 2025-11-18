# Service: AI Analyzer

This is the "Brain" of the architecture. It consumes batched text from the intake queue and uses Google Gemini to evaluate candidates.

Unlike a standard chatbot, this service enforces **Strict Structured Output**. It doesn't just "chat", it returns a type-safe JSON object that fits our database schema perfectly.

## Tech Stack

- **AI Model:** Gemini (via google-generativeai)
- **Structure Enforcement:** instructor (Patches Gemini to return Pydantic models)
- **Messaging:** RabbitMQ (Pika)
- **Validation:** Pydantic

## Key Architectural Patterns

### 1. Deterministic AI (The "Instructor" Pattern)

We use the **Instructor** library to tame Gemini.

**How it works:** It injects our Pydantic schema into the prompt and handles the retry logic if Gemini outputs broken JSON.

**Why:** This prevents Data Poisoning. If the AI hallucinates a field that doesn't exist, the validation layer kills it before it hits our database.

### 2. Externalized Prompts

We don't hardcode system instructions.

The service loads the "AI Persona" from `config/prompt_system_instruction.txt`.

**Benefit:** You can tweak the grading criteria by editing a text file, without touching the Python code.

### 3. Backpressure & Rate Limiting

AI is slow (I/O heavy).

**Throttling:** We enforce a 5-second delay per job to stay within the Gemini Free Tier limits.

**Load Balancing:** We set `channel.basic_qos(prefetch_count=1)`. This ensures the worker never hoards messages. If we spin up 5 workers, the load balances perfectly based on inference speed.

## 🔄 Logic Flow

1. **Consume:** Get a batch of CVs + Job Description from `QUEUE_AI_ANALYSIS`.

2. **Wait:** Sleep for 5s (Cost Control).

3. **Inference:** Call Gemini with `temperature=0.1` (because we want an Analyst).

4. **Validation:**
   - ✅ **Pass:** Inject cv_id metadata back into the result and publish to `QUEUE_RESULTS_STORAGE`.
   - ❌ **Fail:** Publish an error report. We do not crash the worker for one bad file.

## Input / Output Contracts

### Consumes (QUEUE_AI_ANALYSIS)

```json
{
  "job_id": "job_123",
  "correlation_id": "abc-xyz",
  "jd_text": "Senior Python Developer...",
  "use_delay": true,
  "cvs": [
    {
      "cv_id": "job_123_001",
      "text": "Extracted CV text content...",
      "filename": "resume.pdf",
      "original_filename": "resume.pdf"
    }
  ]
}
```

### Produces (QUEUE_RESULTS_STORAGE)

The result is a clean, database-ready JSON object.

```json
{
  "job_id": "job_123",
  "correlation_id": "abc-xyz",
  "cv_id": "job_123_001",
  "status": "success",
  "data": {
    "candidate_name": "John Doe",
    "match_score": 85,
    "summary_headline": "Strong Backend Candidate",
    "skill_gaps": ["RabbitMQ"],
    "recommendation": "Interview"
  }
}
```
