# Operations AI

Operations AI is a grounded process-data assistant. The initial application accepts a CSV, validates one numeric duration column, computes deterministic statistics, and prepares a typed evidence package for a three-stage AI workflow.

## Architecture

```text
Streamlit GUI / FastAPI
        |
        v
Application orchestration
        |
        +--> CSV validation --> deterministic statistics
        |
        +--> AI analyst --> interpreter --> critic
        |
        v
Typed evidence and result models
```

The numerical analysis never depends on an LLM. AI stages consume computed evidence through typed schemas and will be implemented behind a single client boundary.

## Local setup

1. Install Python 3.11 or newer.
2. Create and activate a virtual environment.
3. Install the project:

   ```powershell
   python -m pip install -e ".[dev]"
   ```

4. Copy `.env.example` to `.env` and add your personal OpenAI API key. Never commit `.env`.
5. Start the GUI:

   ```powershell
   streamlit run ui/streamlit_app.py
   ```

6. Optionally start the API:

   ```powershell
   uvicorn app.api.main:app --reload
   ```

## Development

Run all checks with:

```powershell
pytest
ruff check .
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for module ownership and extension rules.
