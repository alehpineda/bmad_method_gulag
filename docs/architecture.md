# Architecture Document: Pokedex ETL Fullstack MVP (v1.2 - API & ETL Design)

## Overview
**System Vision**: Monolithic greenfield app: Typer ETL → 3NF SQLite DB → FastAPI API → HTMX/Tailwind UI. MVP: Single Pokemon ETL/display from PokeAPI core fields. Scalable to multi-Pokemon.

**Key Components**:
- **ETL Layer**: Typer CLI fetches/parses JSON (httpx async), normalizes to DB (idempotent inserts).
- **DB Layer**: SQLite with SQLModel (3NF schema v1.1 with indexes for <100ms queries).
- **API Layer**: FastAPI REST (MVP GET endpoints with Pydantic; joins for types/stats/sprites).
- **UI Layer**: Static HTMX SPA (AJAX to API for load/toggles; Tailwind Gen 1 theme).
- **Tools**: uv (env), SQLAlchemy (ORM), Pytest (tests), httpx (async fetch).

**Non-Functional Alignment** (from PRD/risk-nfr.md): Performance (<5s ETL, <100ms API via async/indexes); Reliability (null handling, idempotency); Maintainability (Modular: src/etl/main.py, src/api/main.py, public/ui/index.html).

## Data Model (3NF Schema)
[Unchanged from v1.1: Tables pokemon, types, pokemon_types, pokemon_stats, sprites with indexes (e.g., idx_pokemon_name, idx_sprites_pokemon). See previous sections for details/SQLModel classes/schema.sql.]

## API Design
FastAPI endpoints for MVP read-only CRUD (focus: GETs with schema joins). Uses SQLModel for queries (joinedload avoids N+1); Pydantic for validation/serialization. Optionals (null sprite URLs) explicit in response (UI fallbacks). Errors: HTTP 404/500 with JSON details. Indexes ensure perf (e.g., name lookup <10ms).

**Endpoints** (Implement in `src/api/main.py`; Depends: `from sqlmodel import Session, select, joinedload`; Pydantic in `src/schemas.py`):
- **GET /pokemon/{identifier}** (identifier: int ID or str name, e.g., /pokemon/1 or /pokemon/bulbasaur):
  - Query: `session.exec(select(Pokemon).where(or_(Pokemon.id == id, Pokemon.name == identifier)).options(joinedload(Pokemon.types), joinedload(Pokemon.stats), joinedload(Pokemon.sprites))).first()`.
  - Response: PokemonResponse (Pydantic; converts units, lists types/stats, dict sprites {variant: url or null}).
  - Example (Bulbasaur): 
    ```json
    {
      "id": 1,
      "name": "bulbasaur",
      "height_m": 0.7,
      "weight_kg": 6.9,
      "types": [{"name": "grass", "slot": 1}, {"name": "poison", "slot": 2}],
      "stats": [{"name": "hp", "base_stat": 45}, ... (6 total)],
      "sprites": {"front_default": "https://...", "front_shiny": "https://...", "back_default": null, ...}
    }
    ```
  - Perf: Indexed joins <50ms (SQLite single-row).
  - Errors: 404 {"detail": "Pokemon not found"} if none; 500 {"detail": "Query error"} on DB fail.

- **GET /pokemon/{id}/sprites/{variant}** (e.g., /pokemon/1/sprites/front_shiny; variant: str):
  - Query: `session.exec(select(Sprite).where(and_(Sprite.pokemon_id == id, Sprite.variant == variant))).first()`.
  - Response: SpriteResponse (Pydantic): `{"url": "https://..." or null, "available": true/false}`.
  - Handles nulls: Returns null if missing (e.g., back_female for Bulbasaur); UI shows default.
  - Perf: Direct index hit <10ms.
  - Errors: 404 {"detail": "Sprite not found"} if Pokemon/variant invalid.

**Pydantic Models** (src/schemas.py stub in impl):
```python
from pydantic import BaseModel
from typing import List, Optional, Dict

class Stat(BaseModel):
    name: str
    base_stat: int

class TypeInfo(BaseModel):
    name: str
    slot: int

class Sprite(BaseModel):
    variant: str
    url: Optional[str]

class PokemonResponse(BaseModel):
    id: int
    name: str
    height_m: float
    weight_kg: float
    types: List[TypeInfo]
    stats: List[Stat]
    sprites: Dict[str, Optional[str]]  # Variant -> URL (null if unavailable)
```

**Risks Addressed**: CRUD reliability (Pydantic 404s); Data inconsistency (unit conversions in response); Perf (indexed queries).

## ETL Design
Typer CLI for batch ETL (`typer run etl load --id 1`). Async httpx for PokeAPI GET (timeout 5s); fallback to SAMPLE_BULBASAUR on failure (mitigates limits). Parse extracts core (skip null sprites); normalize to 3NF (types first for FKs). Idempotent: Skip if pokemon.id exists. <5s: Async fetch ~1s, parse/insert ~2s (batch SQLite).

**Flow Diagram** (Mermaid in doc; ASCII here):
```
[CLI: etl load 1] --> [Async Fetch: GET /pokemon/1 or Sample] --> [Parse: Extract Core (id/name/height/weight/types/stats/sprites)] 
                                                                 |
                                                                 v
[Normalize: Convert Units, Handle Nulls (e.g., skip female if null)] --> [DB Insert: Idempotent (Check Exists → Skip/Add)]
                                                                 |
                                                                 v
[Commit: Transactional (Rollback on Error)] --> [Log: "Inserted Bulbasaur" or "Skipped"]
```

**Pseudocode** (Full logic; implement in src/etl/main.py stub):
```python
import asyncio
import httpx
from sqlmodel import Session, select
from models import *  # Pokemon, etc.
from typing import Dict, Any

SAMPLE_DATA = { ... }  # Static Bulbasaur JSON for fallback

async def fetch_pokemon(identifier: int) -> Dict[str, Any]:
    url = f"https://pokeapi.co/api/v2/pokemon/{identifier}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        print(f"Fetch failed: {e}; using sample.")
        return SAMPLE_DATA

def normalize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    # Parse core fields; convert units if needed (but store raw in DB, convert in API)
    normalized = {
        "id": data["id"],
        "name": data["name"],
        "height": data["height"],  # decimeters
        "weight": data["weight"],  # hectograms
        "types": [{"name": t["type"]["name"], "slot": t["slot"]} for t in data["types"]],
        "stats": [{"name": s["stat"]["name"], "base_stat": s["base_stat"]} for s in data["stats"]],
        "sprites": {k: v for k, v in data["sprites"].items() if v is not None}  # Skip nulls
    }
    # Validate: Ensure 6 stats, 1-2 types, etc. (from requirements)
    if len(normalized["stats"]) != 6:
        raise ValueError("Invalid stats count")
    return normalized

def insert_idempotent(session: Session, norm_data: Dict[str, Any]):
    # Check existence
    existing = session.exec(select(Pokemon).where(Pokemon.id == norm_data["id"])).first()
    if existing:
        return  # Idempotent: Skip if present

    # Insert Pokemon
    pokemon = Pokemon(**{k: v for k, v in norm_data.items() if k in ["id", "name", "height", "weight"]})
    session.add(pokemon)
    session.flush()

    # Types (upsert)
    for t in norm_data["types"]:
        typ = session.exec(select(Type).where(Type.name == t["name"])).first()
        if not typ:
            typ = Type(name=t["name"])
            session.add(typ)
            session.flush()
        pt = PokemonType(pokemon_id=pokemon.id, type_id=typ.id, slot=t["slot"])
        session.add(pt)

    # Stats
    for s in norm_data["stats"]:
        stat = PokemonStat(pokemon_id=pokemon.id, stat_name=s["name"], base_stat=s["base_stat"])
        session.add(stat)

    # Sprites (only if URL present; validate non-null)
    for variant, url in norm_data["sprites"].items():
        if url:  # Address risk: Validate nulls
            sprite = Sprite(pokemon_id=pokemon.id, variant=variant, url=url)
            session.add(sprite)

    session.commit()

# Main CLI flow
async def etl_load(identifier: int):
    data = await fetch_pokemon(identifier)
    norm = normalize_data(data)
    with Session(engine) as session:
        insert_idempotent(session, norm)
    print(f"ETL complete for {identifier} in <5s.")

# Typer integration: typer run etl load --id 1
```

**Risks Addressed**: API limits (fallback sample); Optionals (skip null sprites); Perf (async/timeout); Idempotency (existence check).

## Integration
- **ETL → DB**: SQLModel sessions for transactional inserts (rollback on IntegrityError).
- **API → DB**: SQLModel queries with eager loading (joinedload) for joins; indexes ensure perf.
- **UI → API**: HTMX attributes (hx-get="/pokemon/{id}", hx-target="#card") for loads; hx-get="/pokemon/{id}/sprites/{variant}" hx-swap="outerHTML" for toggles (fallback JS if null: defaultUrl).
- Full Flow: CLI `etl load 1` → DB populated → uvicorn API → HTMX UI displays/toggles Bulbasaur.

**Dependencies/Risks** (from PRD): Phase 1 complete; Mitigate API limits with samples. Indexes address perf risks (e.g., query bottlenecks in joins).

**Refinements**: Added indexes for MVP queries (name, joins, variants); No views (simple joins suffice). Future: Composite indexes if multi-Pokemon search added.

Generated by BMad Architect on [Current Date]. Version: v1.2 (API & ETL Design).