# Pokedex MVP - ETL Fullstack Demo

**CRITICAL**: Always follow these instructions first and fallback to additional search and context gathering only if the information here is incomplete or found to be in error.

## Working Effectively
- Bootstrap, build, and test the repository:
  - `pip install uv` (if not already installed)
  - `uv sync --dev` -- installs all dependencies including dev tools. Takes 30-60 seconds. NEVER CANCEL.
  - `uv add python-multipart` -- required for FastAPI Form handling
  - `uv add ruff mypy pytest pytest-cov` -- required dev dependencies if missing

## Build and Test Commands (CI/CD Validation)
Always run these commands in sequence to mimic GitHub Actions:
1. **Lint**: `uv run ruff check .` -- takes <1 second. Currently finds 23 import issues that need fixing.
2. **TypeCheck**: `uv run mypy src/` -- takes ~8 seconds. Currently has 18 type errors in API code.
3. **Tests**: `uv run pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=80` -- takes ~6 seconds. Currently 6 failed, 4 passed with 77% coverage (target is 80%).

**TIMING WARNINGS**:
- Build (uv sync): 30-60 seconds. NEVER CANCEL. Set timeout to 5+ minutes.
- Tests: 6-10 seconds for full suite. NEVER CANCEL. Set timeout to 2+ minutes.

## Running the Application

### Database Setup (Required First)
- The app uses SQLite: `pokedex.db` (auto-created)
- **Load sample data**: 
  ```python
  cd /path/to/repo
  uv run python -c "
  from src.etl.main import *
  from src.models import create_db_and_tables
  create_db_and_tables()
  data = SAMPLE_BULBASAUR
  norm = normalize_data(data)
  with get_session() as session:
      insert_idempotent(session, norm)
  print('ETL completed')
  "
  ```
  - Note: Direct CLI `uv run python src/etl/main.py load 1` currently fails due to Typer compatibility issues.

### Start the API Server
- `uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000`
- API available at: http://localhost:8000
- UI available at: http://localhost:8000/ui
- **WARNING**: API has runtime errors. Current GET /pokemon/1 returns 500 error due to SQLModel relationship issues.

## Validation Scenarios
After making changes, ALWAYS run these validation steps:

### Manual Testing Requirements
1. **Database ETL**: Run the sample data loading script (see above). Verify "ETL completed" message.
2. **API Server**: Start uvicorn server. Should show "Application startup complete."
3. **API Endpoints**: 
   - Test: `curl http://localhost:8000/docs` -- should return Swagger UI
   - Note: `curl http://localhost:8000/pokemon/1` currently fails with 500 error
4. **Static UI**: Open browser to http://localhost:8000/ui/index.html -- should load Pokemon search interface

### Known Issues to Address
- **Ruff**: 23 import errors (unused imports in src/api/main.py, src/models.py, tests/)
- **MyPy**: 18 type errors in API relationships and SQLModel usage
- **Pytest**: 6 failing tests due to AttributeError on SQLModel relationships
- **API**: Runtime errors in Pokemon endpoint due to relationship loading issues
- **Typer CLI**: ETL command line interface broken (compatibility issue)

## Troubleshooting
- **DB not found**: Run the sample data script first (tables auto-created)
- **Port in use**: Change --port in uvicorn command
- **Import errors**: Ensure running from project root; src/ has __init__.py files
- **Coverage low**: Current coverage is 77%, target is 80%. Tests fail due to API issues.
- **Dev tools missing**: Run `uv sync --dev` and install missing packages individually
- **Playwright browser errors**: E2E tests fail due to missing browser downloads (network issues)

## Tech Stack
- **Backend**: FastAPI, SQLModel, Alembic (migrations), Typer (CLI - currently broken)
- **Database**: SQLite (pokedex.db)
- **Frontend**: Vanilla JS + HTMX, Tailwind CSS (static in public/ui)
- **Tools**: uv (Python package manager), Ruff (linter), MyPy (type checker), Pytest (tests)
- **Python**: Requires 3.12+

## Project Structure
- `src/api/`: FastAPI app with Pokemon endpoints
- `src/etl/`: Data loading scripts (CLI currently broken)
- `src/models.py`: SQLModel schemas for Pokemon, Type, Sprite, etc.
- `src/schemas.py`: Pydantic response models
- `public/ui/`: Static HTML/JS/CSS for Pokemon search interface
- `tests/`: Unit tests (API, ETL) and E2E tests (Playwright)
- `docs/`: PRD, architecture, runbook documentation
- `.github/workflows/ci.yaml`: GitHub Actions CI pipeline

## Repository Root Directory Structure
```
.
├── .bmad-core/              # BMad Method framework files
├── .bmad-infrastructure-devops/  # DevOps expansion pack
├── .github/
│   └── workflows/ci.yaml    # CI pipeline
├── docs/                    # Architecture, PRD, runbook
├── public/ui/               # Static frontend
├── src/
│   ├── api/                 # FastAPI application
│   ├── etl/                 # Data loading scripts
│   ├── models.py            # SQLModel database schemas
│   └── schemas.py           # Pydantic response models
├── tests/                   # Test suite
├── pyproject.toml           # Python project config
├── uv.lock                  # Dependency lock file
└── README.md                # Quick start guide
```

## Performance Expectations
- **uv sync**: 30-60 seconds for full dependency resolution
- **Database ETL**: <1 second for single Pokemon sample data
- **API startup**: 2-3 seconds until "Application startup complete"
- **Lint/Typecheck**: <10 seconds combined
- **Test suite**: 6-10 seconds (currently failing, expect longer when fixed)
- **UI load**: Instant (static files)

## Common Commands Reference
```bash
# Complete setup from fresh clone
pip install uv
uv sync --dev
uv add python-multipart ruff mypy pytest pytest-cov

# Load sample data (required before API testing)
uv run python -c "from src.etl.main import *; from src.models import create_db_and_tables; create_db_and_tables(); data = SAMPLE_BULBASAUR; norm = normalize_data(data); with get_session() as session: insert_idempotent(session, norm); print('ETL completed')"

# Start development server
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Run all CI checks
uv run ruff check .
uv run mypy src/
uv run pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=80

# Clean restart (if needed)
rm -rf .venv pokedex.db
uv sync --dev
```

## For External AI Coding Assistants
- The codebase has several known issues that need fixing before full functionality
- Focus on SQLModel relationship loading errors in the API layer
- Type errors in src/api/main.py are blocking proper functionality
- The ETL CLI needs Typer compatibility fixes
- Test coverage is currently 77% and needs to reach 80%
- Always test your changes with the validation scenarios above