# GitHub Issues Backlog

## Bugs
1. **Repository file locking** — concurrent writes to `results.json` can clobber content when multiple workers run simultaneously. Investigate file locks or move to SQLite/Postgres (labels: bug, high).
2. **Case-sensitive keyword detection** — analyzer lowercases tokens but not metadata; some keywords slip through (labels: bug, medium).

## Improvements
1. **Result pagination in API** — `/candidates` returns the full dataset; add pagination & filtering (labels: enhancement, good-first-issue).
2. **Config validation** — guard against invalid YAML keys to catch typos earlier (labels: enhancement).
3. **Better sample data** — ship a curated set of anonymized resumes for demos/tests (labels: docs, enhancement).

## Features
1. **Async task queue** — offload heavy analysis to worker pool (labels: feature, roadmap-mid).
2. **Structured exporter** — push normalized candidates into Airtable/Sheets (labels: feature, integration).
3. **Notification hooks** — emit Slack/email when a new high-scoring candidate arrives (labels: feature, community).
