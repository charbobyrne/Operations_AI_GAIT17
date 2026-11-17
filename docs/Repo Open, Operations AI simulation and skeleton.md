# Repo Open, Operations AI simulation and skeleton

## Handoff purpose

Machine-oriented repository state for developers and their coding agents. Read `AGENTS.md`, `docs/ARCHITECTURE.md`, and `docs/DEVELOPMENT_LOG.md` before making changes.

## Current product direction

Build a grounded operations-data assistant that accepts a CSV, validates one numeric process-duration column, computes evidence deterministically, and uses three bounded AI stages to explain and critique the result. The application must not claim a bottleneck without arrival and resource data. Human confirmation remains required before operational action.

## Current repository state

- Branch: `main`.
- Initial skeleton commit: `8b83681 Setup and Skeleton commit`.
- Runtime: Python 3.11+.
- UI: Streamlit guided test console.
- Optional HTTP boundary: FastAPI health endpoint.
- AI provider: OpenAI Responses API with Pydantic structured outputs.
- State: in-memory Streamlit session state; JSON reports are downloadable but ignored by Git.
- Data: bundled CC0 synthetic call-center dataset, 800 rows; default field is `handle_seconds`.

## Architecture map

```text
ui/streamlit_app.py
        |
        v
app/orchestration/pipeline.py
        |
        +--> app/data/csv_loader.py
        +--> app/analysis/statistics.py
        +--> app/ai/stages.py --> app/ai/client.py --> OpenAI
        |
        v
app/core/models.py
```

Rules: deterministic calculations do not import AI code; provider access stays behind `AIClient`; UI owns presentation only; orchestration selects offline or live stages.

## Implemented behavior

1. The UI initially exposes only Test; Dashboard, Simulations, and Reports are disabled placeholders.
2. Start environment verifies bundled data, local API-key presence, and configured model. Instantiating the client does not make an API request.
3. A user selects the bundled CSV or uploads another CSV.
4. Numeric candidate columns are detected; the user selects a duration field and unit.
5. Deterministic analysis excludes blank, non-numeric, zero, and negative values.
6. Offline mode returns explicit placeholder stages without API usage.
7. OpenAI mode calls analyst, interpreter, and critic exactly once each.
8. Results show descriptive statistics, stage summaries/warnings, raw evidence, API token usage, and a JSON download.

## API safety invariants

- Key is loaded from untracked `.env`; `.env.example` contains no secret.
- Maximum calls per `OpenAIClient` instance: 3.
- SDK automatic retries: 0.
- Maximum output tokens per call: 500 by default, schema-limited to 1000 maximum.
- Maximum evidence payload: 20,000 characters by default, schema-limited to 50,000 maximum.
- Timeout: 30 seconds by default, schema-limited to 60 seconds maximum.
- Automated tests never use a live API key.
- `tests/test_ai_safety.py` verifies the fourth call and oversized payload are rejected before network access.

Do not add loops, recursion, retry wrappers, fan-out, or background API execution. Any change to these limits requires explicit team review and a development-log entry.

## Known baseline from bundled data

- Input rows: 800.
- Valid `handle_seconds`: 695.
- Blank exclusions: 105 abandoned calls.
- Mean: 217.39 seconds.
- Median: 196 seconds.

These values are useful regression checks.

## Important files

- `AGENTS.md`: mandatory repository and API-safety rules.
- `README.md`: human setup and test instructions.
- `docs/DEVELOPMENT_LOG.md`: append-only change history.
- `docs/ARCHITECTURE.md`: module boundaries and suggested ownership.
- `ui/streamlit_app.py`: guided test console.
- `scripts/run_e2e_demo.py`: CLI equivalent of the pipeline.
- `app/core/config.py`: environment configuration and hard safety bounds.
- `app/ai/client.py`: only live provider adapter.
- `app/ai/stages.py`: prompts and stage sequencing.
- `tests/test_ai_safety.py`: cost/runaway protections.
- `sample_data/README.md`: dataset provenance and license.

## Recommended developer split

- Developer 1: distribution fitting, diagnostics, and deterministic evaluation fixtures.
- Developer 2: prompt/version evaluation, grounding scores, latency/cost comparison, and AI schemas.
- Developer 3: GUI refinement, session persistence, plots, and integration.

All developers update tests and `docs/DEVELOPMENT_LOG.md` with their changes.

## Next implementation sequence

1. Add SciPy candidate fits without changing the AI boundary.
2. Extend `EvidencePackage` with fit diagnostics.
3. Create fixed evaluation fixtures and expected grounding rules.
4. Compare at least two configured models on quality, latency, and token usage.
5. Add grounded follow-up questions using stored evidence only.
6. Add persistence only after the core pipeline and evaluation suite are stable.

## Validation commands

```powershell
python -m pytest
python -m ruff check .
python -m compileall -q app ui scripts
python scripts/run_e2e_demo.py --offline
```

The live demo is manually initiated with `python scripts/run_e2e_demo.py` or through the GUI OpenAI mode. Do not run it in CI.
