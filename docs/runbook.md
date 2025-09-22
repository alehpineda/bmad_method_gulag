# Pokedex MVP Runbook

## Environment Setup
1. Clone the repo: `git clone &lt;repo-url&gt;`
2. Navigate: `cd bmad_method_gulag`
3. Install Python 3.12+ and uv: Follow https://docs.astral.sh/uv/getting-started/installation/
4. Sync dependencies: `uv sync`
5. (Optional) Set up virtual env if not using uv: `uv venv && source .venv/bin/activate`

## Database Initialization
- The app uses SQLite: `pokedex.db` (created on first run or via ETL)
- Run ETL to populate: `uv run python src/etl/main.py load 1` (loads Bulbasaur)

## Running the Application
1. Start the server: `uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000`
   - Serves API at http://localhost:8000
   - Serves static UI at http://localhost:8000/ui
2. Verify API: `curl http://localhost:8000/pokemon/1`
   - Should return JSON with Bulbasaur details

## Testing E2E
1. Load data: `uv run python src/etl/main.py load 1`
2. Start app (as above)
3. Test API: `curl http://localhost:8000/pokemon/1 | jq .name` → "bulbasaur"
4. Test UI:
   - Open http://localhost:8000/ui/index.html
   - Enter "1" in input, submit → Displays Bulbasaur card with stats, types, sprites
   - Toggle shiny button → Switches to shiny sprite if available

## CI/CD Validation (Local)
Run these to mimic GitHub Actions:
1. Lint: `uv run ruff check .`
2. Typecheck: `uv run mypy src/`
3. Tests: `uv run pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=80`
4. Build: `uv sync --dev`

## Deployment
### Local
As above.

### Railway (Backend)
1. `npm i -g @railway/cli`
2. `railway login`
3. `railway init` (link to project)
4. `railway up` (deploys from current dir)
- Env vars: None needed for SQLite, but for prod use Railway Postgres if scaling.

### Netlify (UI Static)
1. `npm i -g netlify-cli`
2. `netlify login`
3. `netlify deploy --prod --dir=public/ui`
- Post-deploy: Update index.html JS fetch URL to your Railway API (e.g., https://your-railway.app)

## Troubleshooting
- DB not found: Run ETL first.
- Port in use: Change --port.
- Coverage low: Run `uv run pytest --cov=src` to check.
- For more Pokemon: Edit ETL to load range, e.g., load 1-151.

## Monitoring & Logs
- Uvicorn logs to console.
- For prod, add logging to files or integrate Sentry.

MVP is ready for demo: Load Bulbasaur via UI and verify toggles work.