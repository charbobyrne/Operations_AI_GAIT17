# Architecture and team conventions

## Boundaries

- `app/data`: file parsing and column discovery only.
- `app/analysis`: deterministic calculations. It must not import `app/ai`.
- `app/ai`: provider adapters, prompts, and structured AI stages.
- `app/orchestration`: coordinates data, analysis, and AI stages.
- `app/api`: stable HTTP entry points for future clients.
- `ui`: presentation and user interaction. Business logic does not belong here.

## Suggested ownership

| Area | Primary owner | First milestone |
| --- | --- | --- |
| Data and statistics | Developer 1 | Validation, distribution fits, test fixtures |
| AI and evaluation | Developer 2 | OpenAI adapter, prompts, quality/cost benchmark |
| GUI and integration | Developer 3 | Review flow, charts, session state, API wiring |

Ownership means coordination responsibility, not exclusive access. Every pull request should be reviewed by a developer who does not own that area.

## Non-negotiable design rules

1. Deterministic values are calculated in Python and never by an LLM.
2. AI stages accept typed evidence instead of unrestricted raw application state.
3. Every model response must be validated against a Pydantic schema.
4. The final output must identify missing operational inputs and unsupported claims.
5. Model name, prompt version, latency, tokens, and estimated cost will be recorded for evaluations.
6. API keys remain in each developer's untracked `.env` file.

## Next implementation milestones

1. Add candidate distribution fitting and fit diagnostics to `app/analysis`.
2. Define versioned response schemas and evaluation cases for each AI stage.
3. Implement the OpenAI adapter with structured outputs, usage telemetry, and timeouts.
4. Replace placeholder stages one at a time while retaining deterministic fallbacks.
5. Add persistence for user confirmations and grounded follow-up questions.
