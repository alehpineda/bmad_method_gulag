# Greenfield Fullstack Workflow Plan: Pokedex ETL Service Demo (v1.1)

## Overview
This plan outlines the execution of the **Greenfield Fullstack Workflow** for the Pokedex ETL service project, based on the idea in `docs/idea.md`. The goal is to demonstrate the BMAD method end-to-end for a real agile fullstack team: Fetch Pokemon data from PokeAPI via ETL batch job, normalize into SQLite (3NF), expose via FastAPI CRUD API, and display in a Gen 1-themed single-page app (HTMX + Tailwind) with sprite toggles.

- **Epic**: Build Pokedex ETL Fullstack Demo.
- **MVP Scope**: Core Pokemon info (id, name, height, weight, types, sprites, stats: hp/attack/defense/special-attack/special-defense/speed). Single Pokemon view; sprite buttons (default front, female/shiny/gens if available).
- **Tech Stack**: Python 3.12+ (Typer for ETL, FastAPI for API, SQLModel/SQLAlchemy for DB), SQLite, HTMX/Tailwind for UI, uv (env), Ruff/Mypy/Pytest (quality).
- **Assumptions**: Small team (1-3 devs), part-time; Use sample JSONs (docs/1.json etc.) for initial schema/ETL dev; PokeAPI docs: https://pokeapi.co/docs/v2.
- **Success Criteria**: ETL loads data; API CRUD works; UI displays/toggles sprites; Tests >80% coverage; Docs complete; Locally deployable.
- **Risks/Mitigations**: API limits (mock with JSONs); Normalization complexity (use SQLModel); HTMX learning (docs: https://htmx.org/docs/, https://tailwindcss.com/docs).
- **Timeline**: 2-3 weeks (2-3 sprints, 1 week each); Parallel tracks for faster overlap.
- **Tracking**: Use BMAD commands (*status, *plan-update); Git for version control. Parallelism: Assign epics to team members; Use *task create-next-story for dynamic backlog.

## Epics Overview
To enable parallelism:
- **Epic 1: Project Foundations** – Sequential setup (all must complete before parallel work).
- **Epic 2: Backend Foundations** – ETL + API (parallel after DB schema).
- **Epic 3: Frontend Experience** – UI design/build (design parallel with backend; build after API).
- **Epic 4: Integration & Quality** – Cross-epic testing/deployment (parallel with late implementation).

## Phases & Stories

### Phase 1: Discovery & Planning (Sprint 0; 2 days)
**Objectives**: Bootstrap project bases, align on reqs, create docs, build backlog. First story sets up everything.

- **Story 1.0: Project Setup (Bases for Whole Project)**  
  Tasks: Init Git repo; Setup uv virtual env; Install deps (FastAPI, SQLModel, Typer, HTMX/Tailwind via CDN or build); Create basic structure (src/etl, src/api, public/ui, tests/); Config tools (Ruff/Mypy/Pytest); Add .gitignore/README.md with setup instructions. Commit initial scaffold.  
  AC: Env activates/runs; Basic "hello world" API/UI endpoints work; Linting passes.  
  Agents: Dev (lead), Infra-DevOps-Platform (CI basics).  
  Tools: Bash for setup; *agent dev for structure.  
  Outputs: Working repo/env; Initial commit.  
  Timeline: Day 1 (Sequential – Run this FIRST).  
  Parallelism: N/A – Foundation for all.

- **Story 1.1: Elicit & Document Requirements**  
  Tasks: Review PokeAPI; Analyze JSON samples for fields; Define MVP (no evolutions/moves).  
  AC: Requirements doc traces API fields to app features.  
  Agents: Analyst (lead), PO.  
  Tools: *task advanced-elicitation; Read JSONs.  
  Outputs: Requirements trace.  
  Timeline: Day 1 (Parallel with 1.0 after setup).  

- **Story 1.2: Create PRD & Project Brief**  
  Tasks: Draft PRD (stories, NFRs: ETL <5s/Pokemon, UI accessible); Brainstorm UI (sprite toggles).  
  AC: PRD covers epics with parallel tracks noted.  
  Agents: PM (lead), UX-Expert.  
  Tools: *task create-doc (prd-tmpl.yaml).  
  Outputs: docs/prd.md (v1); Wireframes.  
  Timeline: Day 2 (Parallel with 1.3).  

- **Story 1.3: Risk & NFR Assessment**  
  Tasks: Profile risks (data parsing); Assess perf/security.  
  AC: Risks prioritized; Mitigations assigned to epics.  
  Agents: QA (lead), Architect.  
  Tools: *task risk-profile; *task nfr-assess.  
  Outputs: Risk matrix in PRD.  
  Timeline: Day 2.

**Milestone**: Backlog ready; Parallel epics defined. QA Gate: Initial review.

### Phase 2: Architecture & Design (Sprint 1; 3-4 days)
**Objectives**: Design DB/API/UI; Normalize to 3NF. Parallel: UI design with backend schemas.

- **Epic 2: Backend Foundations**  
  - **Story 2.1: Design DB Schema**  
    Tasks: Tables: pokemon (id/name/height/weight), pokemon_types (junction), pokemon_stats (hp/etc.), sprites (JSON/variants).  
    AC: Schema script creates 3NF DB; Validates against sample JSON.  
    Agents: Architect (lead), Dev.  
    Tools: *task create-doc (architecture-tmpl.yaml).  
    Outputs: docs/architecture.md (DB section); Schema script.  
    Timeline: Days 1-2 (Dependency for Epic 2/3).  
    Parallelism: UI design (Story 2.3) can start concurrently.

  - **Story 2.2: API & ETL Design**  
    Tasks: Endpoints (/pokemon/{id or name}); Typer job (fetch/parse/insert).  
    AC: Specs include error handling for API limits.  
    Agents: Architect (lead), Dev.  
    Tools: Pydantic models.  
    Outputs: API spec; ETL diagram.  
    Timeline: Days 2-3 (Parallel with UI design).

- **Epic 3: Frontend Experience**  
  - **Story 2.3: UI/UX Design**  
    Tasks: Wireframe Pokedex layout (card, stats bars, HTMX toggles); Tailwind styles.  
    AC: Mockup shows sprite toggle flow.  
    Agents: UX-Expert (lead).  
    Tools: *task generate-ai-frontend-prompt.  
    Outputs: front-end-spec.md; HTML mockup.  
    Timeline: Days 1-4 (Parallel track: Starts early, overlaps backend).

**Milestone**: Designs approved; Parallel epics scaffolded. QA Gate: Design review.

### Phase 3: Implementation (Sprint 2; 4-6 days – With Overlap)
**Objectives**: Build iteratively. Parallel: Backend (Epic 2) and Frontend (Epic 3) tracks.

- **Epic 2: Backend Foundations** (Parallel with Epic 3)  
  - **Story 3.1: Implement ETL Batch Job**  
    Tasks: Typer CLI; Fetch/mocks → SQLModel insert.  
    AC: Job loads sample Pokemon to DB.  
    Agents: Dev (lead).  
    Tools: Write/Edit code; Pytest units.  
    Outputs: src/etl/main.py; Loaded data.  
    Timeline: Days 1-2 (After DB schema).  

  - **Story 3.2: Build FastAPI CRUD API**  
    Tasks: GET/CRUD endpoints; DB integration.  
    AC: API returns Pokemon data via Swagger.  
    Agents: Dev (lead), Architect.  
    Tools: FastAPI; Ruff/Mypy.  
    Outputs: src/api/main.py; Swagger.  
    Timeline: Days 2-4 (Parallel with 3.1 and UI build).

- **Epic 3: Frontend Experience** (Parallel with Backend)  
  - **Story 3.3: Develop UI SPA**  
    Tasks: HTMX for dynamics; Display info/sprites; Tailwind theme.  
    AC: UI fetches/displays one Pokemon; Toggles sprites via API.  
    Agents: Dev (lead), UX-Expert.  
    Tools: Tailwind config.  
    Outputs: public/index.html; CSS/JS.  
    Timeline: Days 3-6 (Design from Phase 2; Build after API ready – overlap testing).

**Milestone**: E2E flow. Daily: *status. Parallelism: 2 devs? One on backend, one on UI.

### Phase 4: Testing & Quality (Sprint 3; 2-3 days)
**Objectives**: Validate & polish. Parallel: Test each epic independently.

- **Epic 4: Integration & Quality**  
  - **Story 4.1: Write & Run Tests**  
    Tasks: Units (parsing/API/UI), Integration (DB), E2E (full flow). Mock API.  
    AC: Coverage >80%; Parallel epic tests pass.  
    Agents: QA (lead), Dev.  
    Tools: *task test-design; Pytest.  
    Outputs: tests/; Coverage report.  
    Timeline: Days 1-2 (Parallel: Backend/UI tests separate).  

  - **Story 4.2: QA Gate & Fixes**  
    Tasks: Trace reqs across epics; Apply issues.  
    AC: All epics pass gate.  
    Agents: QA (lead).  
    Tools: *task apply-qa-fixes; *task trace-requirements.  
    Outputs: Updated code.  
    Timeline: Day 3.

**Milestone**: Quality assured.

### Phase 5: Deployment & Release (Final; 1-2 days)
**Objectives**: Deploy & document. Parallel: CI setup with epic integration.

- **Epic 4: Integration & Quality** (Continued)  
  - **Story 5.1: Setup CI/CD & Deploy**  
    Tasks: GitHub Actions (lint/test/build per epic); Deploy (Railway/Netlify).  
    AC: Pipeline runs on push; App live.  
    Agents: Infra-DevOps-Platform (lead).  
    Tools: Docker optional.  
    Outputs: .github/workflows/; URLs.  
    Timeline: Day 1 (Parallel with docs).  

  - **Story 5.2: Final Docs & Handover**  
    Tasks: Update PRD/Arch; Runbook. Retro on parallel execution.  
    AC: Docs cover epic handoffs.  
    Agents: PM (lead), SM.  
    Tools: *task document-project; *party-mode.  
    Outputs: README.md; Docs bundle.  
    Timeline: Day 2.

**Milestone**: MVP live!

## Timeline Summary
- **Week 1**: Phase 1-2 (Setup/Design; Parallel UI/backend design).
- **Week 2**: Phase 3 (Implement; Parallel epics 2/3).
- **Week 3**: Phases 4-5 (Test/Deploy; Parallel testing) + Buffer.
- **Sprints**: Weekly; Parallel tracks via epic assignment. Use *task create-next-story for backlog.
- **Metrics**: Story points (3-5/story); Velocity via *plan-status; Track parallel efficiency in retros.

## Resources
- **Agents**: Rotate as assigned; *agent [id] to switch.
- **Tasks/Checklists**: BMAD core (e.g., *checklist story-dod-checklist).
- **Templates**: prd-tmpl.yaml, story-tmpl.yaml, etc.
- **Next Action**: Run Story 1.0 (Project Setup).

Generated by BMad Master Orchestrator on [Current Date]. Version: v1.1 (Refined for setup-first + parallelism).