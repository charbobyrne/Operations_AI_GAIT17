# Operations AI Team Execution Plan

## Purpose and completion target

This plan coordinates three developers and three AI stages for the remaining project work. The goal is a reliable demonstration in which a user uploads process-time data, reviews validation decisions, sees deterministic statistics and distribution-fit visualizations, and receives a concise final report that never claims more than the evidence supports.

The core version should remain narrow enough to finish in three one-week sprints. Full discrete-event simulation, optimization, Excel support, and automatic operational decisions remain optional until the core workflow is complete.

## Current baseline

The repository already provides:

- CSV upload and numeric-column selection.
- Validation of blank, non-numeric, zero, and negative durations.
- Deterministic descriptive statistics.
- Data Analyst, Interpreter, and Critic API stages with structured outputs.
- Offline and OpenAI test modes.
- A Streamlit test interface, bundled synthetic call-center data, token-usage reporting, and JSON export.
- Hard API safeguards and tests that prevent unbounded calls and hidden retries.

The largest gaps are distribution fitting, meaningful graphs, stronger stage-specific schemas, systematic model evaluation, and a final output that is organized around a user decision.

## Team operating model

Each developer manages one agent, but ownership is not isolation. The owner maintains that agent's contract, prompt, evaluation cases, and backlog. Every agent must also receive:

- One code or prompt review from another developer.
- One test case contributed by a developer who is not the owner.
- End-to-end review by the Output Agent owner before release.

All three developers may improve any agent. Changes to shared schemas or orchestration require agreement from the downstream owner because one stage's output becomes another stage's input.

```text
User and CSV
    |
    v
Deterministic validation, statistics, and distribution fitting
    |
    v
Agent 1: Data Analyst
    |
    v
Agent 2: Interpreter and Simulation Input Advisor
    |
    v
Agent 3: Output and Grounding Agent
    |
    v
Human-readable report, graphs, limitations, and next steps
```

## Developer 1 - Data Analyst Agent owner

### Mission

Turn the validated dataset and deterministic calculations into a trustworthy data-quality assessment. This agent should explain what the fields appear to represent, identify quality concerns, and ask the user for missing context. It must not calculate statistics or choose a distribution independently of the backend.

### Primary deliverables

- Extend `app/analysis` to fit a small candidate set such as exponential, gamma, lognormal, and Weibull distributions.
- Add fit diagnostics to the evidence package, including sample size, parameters, goodness-of-fit score, rank, and warnings for weak or inconclusive fits.
- Produce chart-ready backend data for a histogram with fitted-density overlays, an empirical CDF comparison, and an outlier or box-plot summary.
- Replace the generic agent result with a Data Analyst schema containing:
  - confirmed observations;
  - data-quality issues;
  - questions requiring user confirmation;
  - prohibited conclusions;
  - evidence references.
- Add fixtures for clean, sparse, constant, skewed, outlier-heavy, and invalid datasets.

### Process recommendations

- Build and test fitting functions before changing the prompt.
- Use fixed synthetic datasets with known properties so regressions are visible.
- Make the agent cite evidence field names rather than copying unstructured numbers into prose.
- Treat a weak fit as a valid result; do not force a winning distribution.
- Send summaries and diagnostics to the model, not the full sensitive CSV.

### Completion checks

- All numerical results can be reproduced without an API key.
- No model-generated number appears in the evidence package.
- Fit rankings and graph inputs have deterministic unit tests.
- The agent asks for units or exclusions when they are not confirmed.

## Developer 2 - Interpreter and Simulation Input Agent owner

### Mission

Explain the computed evidence in operations language and translate an acceptable distribution fit into a possible simulation input. This agent must distinguish what the data shows from what would require arrival, staffing, routing, or resource information.

### Primary deliverables

- Define a structured Interpreter schema containing:
  - plain-language findings;
  - candidate simulation input;
  - assumptions;
  - missing operational inputs;
  - confidence or evidence strength;
  - claims the final stage must not make.
- Version prompts and store the prompt version in evaluation results.
- Create a repeatable evaluation set using representative and adversarial evidence packages.
- Compare at least two approved model configurations on grounding, usefulness, latency, input/output tokens, and estimated cost.
- Add explicit tests for unsupported bottleneck, capacity, causality, and staffing claims.

### Process recommendations

- Evaluate models using the same evidence packages and rubric; do not compare models from informal one-off conversations.
- Score factual support separately from writing quality.
- Reject any response that changes backend numbers or treats missing arrivals/resources as known.
- Keep simulation suggestions conditional: for example, “candidate service-time input” rather than “the process follows this distribution.”
- Record failed prompts and lessons in the development log so the team does not repeat experiments.

### Completion checks

- The same test cases can be run against each configured model.
- Evaluation output includes model, prompt version, latency, tokens, estimated cost, and pass/fail reasons.
- Unsupported operational conclusions are caught by tests.
- The output remains useful when the best-fit result is weak or ambiguous.

## Developer 3 - Output and Grounding Agent owner

This is Charles's primary ownership area.

### Mission

Convert the evidence and prior agent results into an organized, conclusive, and honest final experience. This stage is both the final grounding gate and the report composer. It may organize and simplify supported findings, but it may not introduce new statistics, distributions, or operational facts.

### Primary deliverables

- Replace the generic Critic result with a structured Final Output schema containing:
  - run status: `ready_for_simulation_input`, `needs_more_information`, or `blocked`;
  - executive summary;
  - data-quality conclusion;
  - key supported findings;
  - selected candidate fit and evidence strength;
  - assumptions and missing information;
  - warnings and removed unsupported claims;
  - recommended next steps;
  - short captions or explanations for each deterministic graph.
- Block final display when prior claims conflict with the evidence, and show the user what must be corrected.
- Redesign the results page around a readable hierarchy:
  1. status and executive summary;
  2. data-quality decision;
  3. key metrics;
  4. graphs and fit comparison;
  5. assumptions and missing information;
  6. agent audit trail and API usage.
- Add accessible graph titles, units, legends, color contrast, and concise explanatory captions.
- Keep technical diagnostics available in an expandable section instead of mixing them into the primary conclusion.

### Recommended visualizations

Start with three graphs that answer different questions:

1. **Histogram with fitted-density overlays:** shows the observed shape and how candidate distributions compare.
2. **Empirical CDF versus candidate CDF:** makes tail and cumulative-fit differences easier to see than a histogram alone.
3. **Box plot or outlier strip:** communicates spread and extreme observations without implying that every outlier is an error.

Add a compact fit-comparison table beside the graphs. Do not generate charts with the LLM; create them deterministically from backend results and let the Output Agent explain only the supplied chart metadata.

### Process recommendations

- Design the final output schema before revising the prompt or UI.
- Test the report with both successful and blocked examples.
- Make the first screen understandable to a non-statistician in under one minute.
- Use short conclusions followed by evidence, not a long conversational answer.
- Ensure every final claim can be traced to a backend field or an earlier validated agent field.
- Review both other agents' schemas because the final stage cannot repair missing evidence reliably.

### Completion checks

- A user can identify the main conclusion, limitations, and next action without opening technical tabs.
- The final status is deterministic from validated blocking conditions where possible.
- Graphs render correctly for small samples, skewed data, constant data, and missing values.
- Unsupported claims are removed or visibly blocked before the final report appears.

## Shared backend and frontend contracts

Agree on these contracts before parallel implementation:

- `EvidencePackage` remains the authoritative source for numbers.
- Add typed `DistributionFitResult`, `FitDiagnostics`, and chart-data models.
- Each agent gets a distinct response schema rather than the shared `AIStageResult`.
- Each response includes evidence references or supported-field names.
- The orchestration layer owns stage order, safety limits, timing, and failure handling.
- The UI receives one complete pipeline result and does not recompute statistics.
- Offline mode must produce the same schema shapes as live mode.

Any contract change should update the producer, consumer, offline fallback, tests, and development log in the same pull request.

## Three-sprint schedule

### Sprint 1 - November 24 to November 30: contracts and deterministic evidence

- Agree on the three stage-specific schemas and final report layout.
- Implement candidate distribution fits and deterministic diagnostics.
- Implement chart-data models and initial plots using offline data.
- Create the shared evaluation fixtures and success rubric.
- Demonstrate an offline run from CSV through final report schema.

**Exit condition:** all numerical evidence and graphs work without an API key, and every agent has a typed contract.

### Sprint 2 - December 1 to December 7: agent quality and model evaluation

- Update each agent prompt to its new schema.
- Add grounding and adversarial tests for each stage.
- Compare at least two model configurations using the same rubric.
- Record latency, token usage, estimated cost, and failure reasons.
- Integrate the Output Agent with the new final report interface.

**Exit condition:** the team can show which model configuration was selected and why, and unsupported claims fail the evaluation suite.

### Sprint 3 - December 8 to December 14: integration and demonstration

- Complete the human-readable dashboard and graph explanations.
- Test clean, invalid, ambiguous, and outlier-heavy datasets end to end.
- Freeze core scope; defer optional simulation, optimization, and process discovery.
- Prepare the final report evidence, contribution record, and demonstration script.
- Rehearse the demo from a fresh clone and new `.env` file.

**Exit condition:** a new developer can set up the repository, run the demo, understand the output, and reproduce the recorded evaluation results.

## Shared board and review rules

Use one issue or task per independently testable result. Each task should state:

- owner and reviewer;
- affected agent and modules;
- input and expected output;
- acceptance test;
- API-cost impact;
- documentation or log update required.

Recommended review rotation:

| Primary owner | Required reviewer |
| --- | --- |
| Data Analyst Agent | Interpreter Agent owner |
| Interpreter Agent | Output Agent owner |
| Output Agent | Data Analyst Agent owner |

Keep pull requests small and integrate at least twice per week. Rebase or merge from `main` before starting dependent work. Do not let three long-lived branches redefine shared schemas independently.

## Evaluation scorecard

Use the same scorecard for each representative dataset and model configuration:

| Category | Passing expectation |
| --- | --- |
| Numerical fidelity | Every number matches the evidence package |
| Grounding | No unsupported bottleneck, staffing, arrival, capacity, or causal claim |
| Data quality | Exclusions and uncertainty are visible |
| Fit interpretation | Weak or ambiguous fits remain qualified |
| Final organization | Summary, evidence, limitations, and next steps are easy to find |
| Visualization | Correct values, units, labels, legends, and readable layout |
| Reliability | Structured schema validates; failures are handled visibly |
| Performance | Latency is acceptable for the demo |
| Cost | Tokens and estimated cost are recorded and compared |

A run fails if a backend number changes, an unsupported final claim is displayed, the final schema does not validate, or a blocking critic result is ignored.

## Definition of core project done

The core project is complete when:

- One CSV and one numeric duration variable work end to end.
- Human review confirms units and exclusions.
- Statistics and candidate distribution fits are deterministic and tested.
- The three AI stages have distinct jobs, schemas, and evaluation cases.
- The final output includes an organized conclusion, graphs, assumptions, missing information, and next steps.
- The grounding stage blocks unsupported operational claims.
- At least two model configurations have been compared for quality, latency, and cost.
- API safety limits and offline tests remain intact.
- Setup, contributions, experiments, limitations, and demo steps are documented.

## Scope guardrails

Do not begin full simulation, optimization, Excel import, process discovery, user accounts, or deployment work until every core completion item passes. If time becomes limited, prioritize deterministic evidence, grounding, output clarity, and evaluation over additional features.

## Source-informed decisions

- The [team proposal](../sources/GAIT_Team_17_Project_Proposal_Revised.pdf) defines the core workflow, distribution comparison, three AI stages, grounded output, plots, and human review.
- The [project-design lecture](../sources/Lecture_Slides/GAIT_Lec-08_LLMs_Project-Design.pdf) recommends decomposing the experience, assigning work to the right software or model component, testing each building block independently, and preserving needed state.
- The [TA feedback](../sources/Feedback_From_TA.txt) specifically calls for comparing output quality against model cost.
- The [project requirements](../sources/GAIT-Project-Proposal_F26%20%281%29.pdf) emphasize meaningful AI integrations, concrete evaluation, responsible use, contribution records, a written report, and an actual-result demonstration.
