import asyncio
import typer
from typing import Dict, Any
import httpx
from sqlmodel import Session, create_engine, select
from src.models import Pokemon, Type, PokemonType, PokemonStat, Sprite, engine
from src.schemas import PokemonData

app = typer.Typer(help="Pokedex ETL CLI")

SAMPLE_BULBASAUR = {  # Fallback sample from docs/1.json (truncated for brevity, full in docs/1.json)
    "id": 1,
    "name": "bulbasaur",
    "height": 7,
    "weight": 69,
    "types": [{"slot": 1, "type": {"name": "grass"}}, {"slot": 2, "type": {"name": "poison"}}],
    "stats": [
        {"base_stat": 45, "stat": {"name": "hp"}},
        {"base_stat": 49, "stat": {"name": "attack"}},
        {"base_stat": 49, "stat": {"name": "defense"}},
        {"base_stat": 65, "stat": {"name": "special-attack"}},
        {"base_stat": 65, "stat": {"name": "special-defense"}},
        {"base_stat": 45, "stat": {"name": "speed"}},
    ],
    "sprites": {
        "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
        "front_shiny": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/1.png",
        "back_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/1.png",
        # Note: front_female is null for Bulbasaur, skipped in normalize
    }
}

def get_session():
    return Session(engine)

async def fetch_pokemon(identifier: int) -> Dict[str, Any]:
    """Async fetch Pokemon data from PokeAPI with timeout and fallback."""
    url = f"https://pokeapi.co/api/v2/pokemon/{identifier}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        typer.echo(f"Fetch failed: {e}; using sample data.")
        return SAMPLE_BULBASAUR

def normalize_data(data: Dict[str, Any]) -> PokemonData:
    """Normalize fetched data: extract core fields, validate stats, skip null sprites."""
    normalized = {
        "id": data["id"],
        "name": data["name"],
        "height": data["height"],  # Store as decimeters, convert in API
        "weight": data["weight"],  # Store as hectograms
        "types": [{"slot": t["slot"], "type_name": t["type"]["name"]} for t in data.get("types", [])],
        "stats": [{"stat_name": s["stat"]["name"], "base_stat": s["base_stat"]} for s in data.get("stats", [])],
        "sprites": {k: v for k, v in data.get("sprites", {}).items() if v is not None}  # Skip nulls
    }
    # Validation
    if len(normalized["stats"]) != 6:
        raise ValueError(f"Invalid stats count: expected 6, got {len(normalized['stats'])}")
    if len(normalized["types"]) not in (1, 2):
        typer.echo("Warning: Unusual number of types")
    return PokemonData(**normalized)

def insert_idempotent(session: Session, norm_data: PokemonData):
    """Idempotent insert: Check existence, upsert related entities."""
    # Check Pokemon exists
    existing = session.exec(select(Pokemon).where(Pokemon.id == norm_data.id)).first()
    if existing:
        typer.echo(f"Pokemon {norm_data.id} ({norm_data.name}) already exists; skipping.")
        return

    # Insert Pokemon
    pokemon = Pokemon(id=norm_data.id, name=norm_data.name, height=norm_data.height, weight=norm_data.weight)
    session.add(pokemon)
    session.flush()  # Flush to get ID

    # Upsert Types and PokemonType
    for t in norm_data.types:
        typ = session.exec(select(Type).where(Type.name == t["type_name"])).first()
        if not typ:
            typ = Type(name=t["type_name"])
            session.add(typ)
            session.flush()  # Get type ID
        pt = PokemonType(pokemon_id=pokemon.id, type_id=typ.id, slot=t["slot"])
        # Check if exists to avoid dup
        existing_pt = session.exec(select(PokemonType).where(PokemonType.pokemon_id == pokemon.id, PokemonType.type_id == typ.id)).first()
        if not existing_pt:
            session.add(pt)

    # Insert Stats
    for s in norm_data.stats:
        stat = PokemonStat(pokemon_id=pokemon.id, stat_name=s["stat_name"], base_stat=s["base_stat"])
        # Stats are unique per pokemon/stat_name, so no dup check needed if PK
        session.add(stat)

    # Insert Sprites (only non-null)
    for variant, url in norm_data.sprites.items():
        sprite = Sprite(pokemon_id=pokemon.id, variant=variant, url=url)
        # PK prevents dups
        session.add(sprite)

    session.commit()
    typer.echo(f"Inserted {norm_data.name} (ID: {norm_data.id}) successfully.")

@app.command()
def load(identifier: int, sample: bool = False):
    """Load and insert Pokemon data by ID (use --sample for fallback)."""
    if sample:
        data = SAMPLE_BULBASAUR
    else:
        data = asyncio.run(fetch_pokemon(identifier))
    norm = normalize_data(data)
    with get_session() as session:
        insert_idempotent(session, norm)
    typer.echo("ETL process completed.")

if __name__ == "__main__":
    app()