# Operations AI development log

Add one entry for every meaningful repository change. Keep entries concise and never include API keys or other secrets.

## 2026-11-17 - Repository opening, simulation, and skeleton

### Added

- Created a modular Python application with separate data, deterministic analysis, AI, orchestration, API, and Streamlit UI layers.
- Added CSV parsing, positive-duration validation, exclusion reporting, descriptive statistics, and typed Pydantic evidence models.
- Added a three-stage OpenAI workflow: data analyst, interpreter, and grounding critic.
- Added structured OpenAI Responses API output parsing and token-usage reporting.
- Added a guided Streamlit test console with disabled future modules, environment readiness checks, included/uploaded data selection, offline/OpenAI modes, result tabs, and JSON download.
- Added an 800-row CC0 synthetic call-center dataset and verified its published SHA-256 checksum.
- Added a command-line end-to-end demo and offline execution mode.
- Added unit, orchestration, safety, and Streamlit interaction tests.
- Added hard API safeguards: three calls maximum per run, no SDK retries, finite timeout, bounded input size, and bounded output tokens.
- Added setup documentation, architecture notes, repository rules, screenshots, and an agent-focused handoff.

### Validation

- `python -m pytest`
- `python -m ruff check .`
- `python -m compileall -q app ui scripts`
- Offline end-to-end run using `handle_seconds`
- Streamlit Test -> Start environment -> Offline run interaction test

### Next work

- Add candidate distribution fitting and fit diagnostics.
- Create versioned evaluation cases for model quality, grounding, latency, and cost.
- Add persistent sessions and grounded follow-up questions.
- Decide whether the optional FastAPI boundary is needed for deployment.

## 2026-11-24 - Three-developer execution plan

### Added

- Added `docs/TEAM_EXECUTION_PLAN.md` to coordinate three agent owners while requiring shared review and cross-agent contributions.
- Assigned primary ownership for the Data Analyst, Interpreter and Simulation Input, and Output and Grounding agents.
- Defined recommendations for deterministic distribution fitting, model-quality and cost evaluation, final report structure, graph visualizations, shared schemas, pull-request review, and scope control.
- Added a three-sprint schedule, evaluation scorecard, and core definition of done.

### Validation

- Confirmed local `main` matches `origin/main` before authoring.
- Reviewed the current schemas, orchestration, analysis, UI, tests, proposal, project requirements, TA feedback, checkpoint guidance, and project-design lecture.
- `python -m pytest`
- `python -m ruff check .`

### Next work

- Team reviews and assigns names to each agent-owner role.
- Agree on stage-specific Pydantic schemas before beginning parallel implementation.
- Start Sprint 1 with deterministic distribution fitting, chart data, and offline final-report output.
