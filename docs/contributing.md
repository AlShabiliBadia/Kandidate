# Contributing

We welcome ideas, tests, and fixes. Please follow the workflow below:

1. **Fork & branch** off `main` with a descriptive branch name.
2. **Run quality gates** before opening a PR:
   ```bash
   make format
   make lint
   make test
   ```
3. **Add tests** for every change and update relevant docs.
4. **Open a pull request** describing motivation, testing, and screenshots/logs when applicable.
5. **Stay responsive** to review comments. Automated checks (CI + pre-commit) must be green before merge.

For larger proposals, open an issue first (see `docs/issues.md`) so we can discuss scope and design together.
