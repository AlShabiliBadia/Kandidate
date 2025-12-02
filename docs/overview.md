# Overview

Kandidate is a production-style reference implementation of a modern applicant intelligence engine. The system ingests resumes or form submissions, normalizes the content, applies deterministic analysis rules, and persists the results for downstream consumption.

The goal of this refresh is to provide a portfolio-quality backend that demonstrates:

- Strong Python packaging practices (pyproject, type hints, docs, CLI)
- Operational maturity (logging, configuration, Docker, CI/CD, testing)
- Modularity with clear boundaries between parsing, analyzing, persistence, and delivery layers

Use this document as the entry point before diving into the deeper architectural notes in `architecture.md`.
