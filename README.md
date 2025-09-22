# Pokedex MVP - ETL Fullstack Demo

## Quick Start

### Local Setup
1. Install dependencies: `uv sync`
2. Populate database (load Pokemon #1): `uv run python src/etl/main.py load 1`
3. Run the app (API + UI): `uv run uvicorn src.api.main:app --reload`
   - API at http://localhost:8000
   - UI at http://localhost:8000/ui

### Demo
- Open http://localhost:8000/ui in browser
- Enter "1" to load Bulbasaur card
- Toggle shiny/off to see sprite variants

## Run ETL
To load more Pokemon data:
`uv run python src/etl/main.py load &lt;id&gt;`

## Deploy

### Local Deploy
Already set up as above.

### Cloud Deploy (Optional)
- **Backend (API + DB)**: Use Railway
  1. Install Railway CLI: `npm i -g @railway/cli`
  2. Login: `railway login`
  3. Init project: `railway init`
  4. Deploy: `railway up`
  - Railway will detect FastAPI and SQLite (use Railway's DB if needed).

- **Frontend (Static UI)**: Use Netlify
  1. Install Netlify CLI: `npm i -g netlify-cli`
  2. Login: `netlify login`
  3. Deploy: `netlify deploy --prod --dir=public/ui`
  - Update UI JS to point to your Railway API URL.

## CI/CD
- GitHub Actions in `.github/workflows/ci.yaml` runs on push/PR:
  - Lint (Ruff)
  - Typecheck (MyPy)
  - Tests (Pytest >80% coverage)
  - Build (uv sync)

## Tech Stack
- Backend: FastAPI, SQLModel, Alembic (migrations), Typer (CLI)
- Database: SQLite (pokedex.db)
- Frontend: Vanilla JS + HTMX, Tailwind CSS (static in public/ui)
- Tools: uv (Python package manager), Ruff (linter), MyPy (type checker), Pytest (tests)

## Project Structure
- `src/api/`: FastAPI app
- `src/etl/`: Data loading scripts
- `src/models/`: SQLModel schemas
- `public/ui/`: Static HTML/JS/CSS
- `tests/`: Unit and E2E tests
- `docs/`: PRD, architecture, runbook

For more details, see docs/runbook.md
