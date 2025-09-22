import asyncio
import typer
from typing import Optional
import httpx
from sqlmodel import Session, create_engine, select
from ..models import Pokemon, Type, PokemonType, PokemonStat, Sprite  # Assume models in src/models.py
from ..schemas import PokemonData  # Pydantic for parsed data

app = typer.Typer(help="Pokedex ETL CLI")

SAMPLE_BULBASAUR = {  # Fallback sample from docs/1.json
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
        # Add more variants; null for missing like female
    }
}

engine = create_engine("sqlite:///pokedex.db")
session_maker = Session(engine)

async def fetch_pokemon(id: int) -> dict:
    """Async fetch from PokeAPI or fallback to sample."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"https://pokeapi.co/api/v2/pokemon/{id}")
            resp.raise_for_status()
            return resp.json()
        except Exception:
            typer.echo("API fetch failed; using sample.")
            return SAMPLE_BULBASAUR

def normalize_data(data: dict) -> PokemonData:
    """Parse/normalize core fields; handle optionals."""
    pokemon = {
        "id": data["id"],
        "name": data["name"],
        "height": data["height"],
        "weight": data["weight"],
        "types": [{"slot": t["slot"], "type_name": t["type"]["name"]} for t in data["types"]],
        "stats": [{"stat_name": s["stat"]["name"], "base_stat": s["base_stat"]} for s in data["stats"]],
        "sprites": {k: v for k, v in data["sprites"].items() if v}  # Skip nulls
    }
    return PokemonData(**pokemon)  # Pydantic validation

def insert_idempotent(session: Session, data: PokemonData):
    """Idempotent insert to 3NF tables."""
    # Check if exists
    existing = session.exec(select(Pokemon).where(Pokemon.id == data.id)).first()
    if existing:
        typer.echo(f"Pokemon {data.id} already exists; skipping.")
        return

    # Insert pokemon
    p = Pokemon(id=data.id, name=data.name, height=data.height, weight=data.weight)
    session.add(p)
    session.flush()  # Get ID

    # Types
    for t in data.types:
        type_obj = session.exec(select(Type).where(Type.name == t["type_name"])).first()
        if not type_obj:
            type_obj = Type(name=t["type_name"])
            session.add(type_obj)
            session.flush()
        pt = PokemonType(pokemon_id=p.id, type_id=type_obj.id, slot=t["slot"])
        session.add(pt)

    # Stats (fixed 6)
    for s in data.stats:
        ps = PokemonStat(pokemon_id=p.id, stat_name=s["stat_name"], base_stat=s["base_stat"])
        session.add(ps)

    # Sprites (non-null only)
    for variant, url in data.sprites.items():
        sp = Sprite(pokemon_id=p.id, variant=variant, url=url)
        session.add(sp)

    session.commit()
    typer.echo(f"Inserted Pokemon {data.id}: {data.name}")

@app.command()
def load(ctx: typer.Context, id: int, sample: bool = False):
    """Load Pokemon by ID (API or sample)."""
    data = SAMPLE_BULBASAUR if sample else asyncio.run(fetch_pokemon(id))
    norm = normalize_data(data)
    with session_maker() as session:
        insert_idempotent(session, norm)

if __name__ == "__main__":
    app()