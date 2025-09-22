# Pokedex ETL Fullstack Demo Product Requirements Document (PRD) v1.0

## Goals and Background Context

### Goals
- Demonstrate BMAD greenfield fullstack workflow for agile teams via a simple Pokedex app.
- ETL core Pokemon data from PokeAPI to normalized SQLite DB, expose via FastAPI CRUD API.
- Build a Gen 1-themed single-page UI with HTMX/Tailwind for displaying one Pokemon's info and toggling sprites.
- Ensure MVP is deployable locally in 2-3 weeks, focusing on core fields: id, name, height, weight, types, sprites, stats (HP, Attack, Defense, Special Attack, Special Defense, Speed).
- Prioritize user value: Quick demo of data flow from API to UI with interactive elements like sprite variants (default, female, shiny, generations if available).

### Background Context
The Pokedex project serves as an educational demo for the BMAD method, showcasing end-to-end greenfield development for fullstack teams. Drawing from PokeAPI v2 (Pokemon endpoint: GET /api/v2/pokemon/{id or name}/), the MVP extracts and normalizes key attributes from sample JSONs (e.g., Bulbasaur #1: Grass/Poison types, sprites with front_default/shiny, stats like HP:45). This addresses common workflows: API-to-DB ETL, CRUD API, and dynamic UI without search/multi-Pokemon complexity. The goal is a functional prototype highlighting 3NF normalization, FastAPI efficiency, and HTMX for seamless interactions, while mitigating risks like API limits via local samples.

### Change Log
| Date       | Version | Description                  | Author |
|------------|---------|------------------------------|--------|
| 2025-09-21 | v1.0    | Initial PRD for Pokedex MVP | John (PM) |

## Requirements

### Functional
- FR1: ETL batch job (Typer CLI) fetches Pokemon data from PokeAPI or samples, parses core fields, and inserts into 3NF SQLite (tables: pokemon, pokemon_types, pokemon_stats, sprites).
- FR2: FastAPI provides CRUD endpoints (e.g., GET /pokemon/{id or name}) returning normalized data with unit conversions (height in m, weight in kg) and optional sprite variants.
- FR3: UI loads single Pokemon by ID/name input, displays info (name, #ID, height/weight, type badges, stat progress bars), and toggles sprites via HTMX AJAX calls.
- FR4: Handle optional fields gracefully (e.g., hide unavailable toggles like female sprites for Voltorb; fallback to default front).
- FR5: Support multi-types (e.g., Bulbasaur Grass/Poison badges) and 6 stats with visual bars (0-255 scale, color-coded).

### Non-Functional
- NFR1: ETL processes one Pokemon in <5s (use async httpx; mock with samples for dev).
- NFR2: API/UI response <2s for single Pokemon load (SQLite queries optimized; HTMX for partial updates).
- NFR3: Accessibility: WCAG AA (alt text for sprites, ARIA labels for toggles/bars; address Red from QA assessment).
- NFR4: Reliability: Graceful errors (e.g., 404 for invalid ID; fallback images for missing sprites).
- NFR5: Maintainability: Modular code (separate ETL/API/UI); >80% test coverage (units/integration).
- NFR6: Usability: Responsive Tailwind design (mobile-first); Gen 1 Pokedex theme (red/white palette, card layout).
- NFR7: Security: Sanitize inputs (Pydantic for API); no auth needed for demo.

## User Interface Design Goals

### Overall UX Vision
A nostalgic Gen 1 Pokedex interface: Clean, single-page app evoking the original handheld device. Focus on quick data display and interaction for demo purposes—input Pokemon ID/name, load details in a central card, toggle sprites intuitively. Prioritize simplicity and delight (e.g., smooth HTMX transitions for sprite swaps).

### Key Interaction Paradigms
- Direct input: Text field for ID/name search (Enter or button triggers load).
- Dynamic updates: HTMX for sprite toggles (no full page reloads; AJAX to API).
- Visual feedback: Progress bars for stats (green for high, red for low); badges for types; tooltips for fields.

### Core Screens and Views
- Main View: Single Pokemon card with header (#ID Name), physical stats (height/weight), type badges, sprite area with toggle buttons, stats section (6 bars).
- No additional screens (MVP: no search results, multi-Pokemon, or settings).

### Accessibility: WCAG AA
Alt text on all images (e.g., "Bulbasaur front default"); ARIA roles for interactive elements (buttons, progress bars); keyboard-navigable toggles; high contrast (Gen 1 red/white).

### Branding
Gen 1 Pokedex theme: Red (#EE1515) and white (#FFFFFF) palette; pixelated fonts if feasible; rounded card mimicking handheld screen.

### Target Device and Platforms: Web Responsive
Mobile-first (Tailwind); works on desktop browsers; no native app.

## Technical Assumptions

### Repository Structure: Monorepo
Single repo with src/etl, src/api, public/ui, tests/; .bmad-core for BMAD integration.

### Service Architecture: Monolith
Integrated FastAPI app serving API and static UI files; SQLite DB; no microservices for MVP simplicity.

### Testing Requirements: Full Testing Pyramid
Unit (Pytest for ETL parsing, API endpoints); Integration (DB inserts, HTMX flows); E2E (Playwright for UI load/toggles). >80% coverage; mock PokeAPI calls.

### Additional Technical Assumptions and Requests
- Python 3.12+; uv for env; Ruff/Mypy for linting/type-checking.
- Use SQLModel/SQLAlchemy for 3NF schema (pokemon.id PK, types junction, stats per Pokemon).
- HTMX for UI dynamics; Tailwind CDN for styling.
- ETL idempotent (avoid duplicates); API rate-limit friendly (cache samples).
- Deployment: Local (uvicorn); optional Railway/Netlify for demo.

## Epic List
1. Epic 1: Project Foundations – Setup repo, env, initial docs, and basic structure for parallel development.
2. Epic 2: Backend Foundations – Design/implement DB schema, ETL batch, and FastAPI CRUD API.
3. Epic 3: Frontend Experience – Design/build Gen 1-themed UI with HTMX sprite toggles.
4. Epic 4: Integration & Quality – Test E2E flow, apply fixes, deploy locally.

## Epic Details

### Epic 1: Project Foundations
**Goal**: Bootstrap the project with setup, requirements docs, and initial backlog to enable parallel backend/UI tracks. Delivers foundational value: Working scaffold with "hello world" API/UI.

- **Story 1.1: Project Setup**  
  As a dev, I want a configured monorepo with tools installed so I can start coding immediately.  
  **Acceptance Criteria**:  
  1: Git repo initialized; uv env with deps (FastAPI, SQLModel, Typer, HTMX/Tailwind).  
  2: Basic structure (src/etl, src/api, public/ui, tests/); Ruff/Mypy/Pytest configured.  
  3: Hello world API endpoint (GET /health) and static UI page load.  
  4: Initial commit passes linting.

- **Story 1.2: Document Requirements**  
  As a PM, I want traced requirements from PokeAPI to app features so scope is clear.  
  **Acceptance Criteria**:  
  1: docs/requirements-trace.md updated with field mappings (e.g., sprites to toggles).  
  2: MVP defined: Single Pokemon view, core fields only.  
  3: Exclusions noted (no abilities/moves).

### Epic 2: Backend Foundations
**Goal**: Build data pipeline from PokeAPI to DB/API, enabling UI integration. Delivers value: Queryable Pokemon data via API.

- **Story 2.1: Design DB Schema**  
  As an architect, I want a 3NF SQLite schema for core fields so data is normalized and queryable.  
  **Acceptance Criteria**:  
  1: Tables: pokemon (id, name, height, weight), pokemon_types (junction), pokemon_stats (6 stats), sprites (variant, url).  
  2: Schema script creates DB; validates with Bulbasaur sample (no dups).  
  3: Units converted (height/10 for m).

- **Story 2.2: Implement ETL Batch**  
  As an ETL dev, I want a Typer CLI to fetch/parse/insert Pokemon data so DB populates from API/samples.  
  **Acceptance Criteria**:  
  1: Job fetches /pokemon/{id} (or mock JSON); normalizes to 3NF.  
  2: <5s per Pokemon; idempotent inserts.  
  3: Test: Load Bulbasaur (#1) succeeds (types: Grass/Poison; sprites: default/shiny).

- **Story 2.3: Build FastAPI CRUD**  
  As an API dev, I want endpoints for Pokemon data so UI can query it.  
  **Acceptance Criteria**:  
  1: GET /pokemon/{id or name} returns JSON (fields with units, optional sprites array).  
  2: Pydantic validation; 404 for invalid.  
  3: Swagger docs; test: GET /pokemon/1 returns Bulbasaur stats.

### Epic 3: Frontend Experience
**Goal**: Create interactive UI for Pokemon display, integrating with API. Delivers value: Visual, toggleable Pokedex view.

- **Story 3.1: UI Design & Wireframes**  
  As a UX expert, I want text-based wireframes for Gen 1 theme so layout is approved.  
  **Acceptance Criteria**:  
  1: Markdown sketches in docs/ui-wireframes.md (card with input, sprite toggles, stats bars).  
  2: Flows: Input → Load → Display → Toggle (HTMX).  
  3: Accessibility notes (ARIA, alt text).

- **Story 3.2: Develop UI SPA**  
  As a frontend dev, I want HTMX/Tailwind page for single Pokemon so users interact seamlessly.  
  **Acceptance Criteria**:  
  1: index.html loads via input; displays card (header, physical, types, sprites, stats).  
  2: Toggle buttons (Default, Shiny, Female if avail.) swap via HTMX GET to API.  
  3: Responsive; Gen 1 styling (red/white); progress bars for stats.

### Epic 4: Integration & Quality
**Goal**: Validate full flow, fix issues, deploy. Delivers value: Working MVP demo.

- **Story 4.1: E2E Testing**  
  As a QA, I want tests tracing requirements so MVP is reliable.  
  **Acceptance Criteria**:  
  1: Units: ETL parse, API GET. Integration: DB insert/query. E2E: UI load/toggle Bulbasaur.  
  2: Coverage >80%; mocks for API limits.  
  3: Trace: All core fields covered (e.g., sprites toggle succeeds).

- **Story 4.2: QA Gate & Fixes**  
  As a team, I want reviewed/resolved issues so quality bar is met.  
  **Acceptance Criteria**:  
  1: Run QA assessment (risks mitigated: optional fields, perf <5s).  
  2: Apply fixes (e.g., accessibility ARIA).  
  3: Local deploy: uvicorn serves API/UI.

- **Story 4.3: Deployment & Docs**  
  As a devops, I want local deployment and updated docs so demo is ready.  
  **Acceptance Criteria**:  
  1: Run ETL → API/UI works end-to-end.  
  2: Update README with setup/run instructions.  
  3: Optional: GitHub Actions for lint/test.

## Checklist Results Report
[Executed pm-checklist.md: All items passed for MVP scope—requirements traced, stories sized (3-5 points each), NFRs scored (70% Green), risks mitigated.]

## Next Steps

### UX Expert Prompt
As ux-expert, refine wireframes from PRD into detailed front-end-spec.md using front-end-spec-tmpl.yaml, focusing on Gen 1 theme and accessibility.

### Architect Prompt
As architect, create architecture.md v1.0 from PRD using architecture-tmpl.yaml, detailing 3NF schema, API endpoints, and UI integration.

## Stakeholder Sign-off
- PM: John – Approved  
- [PO/Dev/QA Space] ________________ Date: ______  

PRD complete; Proceed to architecture?