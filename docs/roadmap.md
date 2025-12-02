# Roadmap

## Immediate (0-1 months)
- Harden repository persistence with locking and optional Postgres backend.
- Extend analyzer rules with skill clusters and penalty scoring for missing sections.
- Add CLI UX polish: table output, progress bars, contextual logging.

## Mid-term (1-3 months)
- Introduce background workers using Celery or Dramatiq for asynchronous processing.
- Implement result pagination, filtering, and search endpoints.
- Integrate vector similarity search to deduplicate or cluster candidates.

## Long-term (3+ months)
- Launch a collaborative web dashboard with roles/permissions.
- Add integrations (calendar, ATS sync, Slack notifications).
- Explore fine-tuned LLM workflows with guardrails for redaction and compliance.
