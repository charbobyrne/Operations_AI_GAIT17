# Operations AI repository rules

These rules apply to every developer and coding agent working in this repository.

## Required workflow

1. Read `docs/ARCHITECTURE.md` and the latest entries in `docs/DEVELOPMENT_LOG.md` before changing code.
2. Keep deterministic calculations in `app/analysis`; do not ask an LLM to calculate statistics.
3. Keep provider calls inside `app/ai`; UI code must call the orchestration layer.
4. Add or update tests for every behavior change.
5. Run `python -m pytest` and `python -m ruff check .` before committing.
6. Add a concise entry to `docs/DEVELOPMENT_LOG.md` for every meaningful code, architecture, dependency, data, or documentation change. Include the date, summary, tests run, and next work. Never record secrets.

## API key and cost safety

- This project uses personal OpenAI API keys. Keys belong only in the untracked `.env` file.
- Never print, log, commit, transmit, screenshot, or place an API key in a test fixture.
- API mistakes can create substantial monetary loss. Never add an unbounded loop, recursion, automatic retry loop, background poller, or batch fan-out around an API call.
- Keep SDK retries disabled and preserve the hard limits in `app/core/config.py`: at most three calls per run, bounded input size, bounded output tokens, and a finite timeout.
- Do not raise a cost-safety limit without explicit team review and a development-log entry explaining why.
- Unit and GUI tests must use offline mode, mocks, or fake clients. Tests must never spend API credits.
- A live API smoke test must be manually initiated by a developer and must remain a single bounded pipeline run.

## Repository hygiene

- Preserve `.env.example` as the safe template and keep `.env` ignored.
- Do not commit generated reports from `output/`.
- Record the source and license for added datasets.
- Keep changes small enough for another developer to review and understand.
