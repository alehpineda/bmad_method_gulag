import asyncio
import typer
from typing import Dict, Any
import httpx
from sqlmodel import Session, create_engine, select
from src.models import Pokemon, Type, PokemonType, PokemonStat, Sprite, create_db_and_tables
from src.schemas import PokemonData

# Create typer app
app = typer.Typer(help="Pokedex ETL CLI")

SAMPLE_BULBASAUR = {
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
        "back_shiny": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/shiny/1.png",
    }
}

engine = create_engine("sqlite:///pokedex.db")

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
        "height": data["height"],
        "weight": data["weight"],
        "types": [{"slot": t["slot"], "type_name": t["type"]["name"]} for t in data.get("types", [])],
        "stats": [{"stat_name": s["stat"]["name"], "base_stat": s["base_stat"]} for s in data.get("stats", [])],
        "sprites": {k: v for k, v in data.get("sprites", {}).items() if v is not None}
    }
    if len(normalized["stats"]) != 6:
        raise ValueError(f"Invalid stats count: expected 6, got {len(normalized['stats'])}")
    if len(normalized["types"]) not in (1, 2):
        typer.echo("Warning: Unusual number of types")
    return PokemonData(**normalized)

def insert_idempotent(session: Session, norm_data: PokemonData):
    """Idempotent insert: Check existence, upsert related entities."""
    existing = session.exec(select(Pokemon).where(Pokemon.id == norm_data.id)).first()
    if existing:
        typer.echo(f"Pokemon {norm_data.id} ({norm_data.name}) already exists; skipping.")
        return

    p = Pokemon(id=norm_data.id, name=norm_data.name, height=norm_data.height, weight=norm_data.weight)
    session.add(p)
    session.flush()

    for t in norm_data.types:
        type_obj = session.exec(select(Type).where(Type.name == t["type_name"])).first()
        if not type_obj:
            type_obj = Type(name=t["type_name"])
            session.add(type_obj)
            session.flush()
        
        # type_obj should be a Type object here, no extraction needed
        if type_obj.id is None:
            raise ValueError(f"Type {t['type_name']} was not properly saved to database")
        
        pt = PokemonType(pokemon_id=p.id, type_id=type_obj.id, slot=t["slot"])
        session.add(pt)

    for s in norm_data.stats:
        ps = PokemonStat(pokemon_id=p.id, stat_name=s["stat_name"], base_stat=s["base_stat"])  # type: ignore [arg-type]
        session.add(ps)

    for variant, url in norm_data.sprites.items():
        sp = Sprite(pokemon_id=p.id, variant=variant, url=url)  # type: ignore [arg-type]
        session.add(sp)

    session.commit()
    typer.echo(f"Inserted {norm_data.name} (ID: {norm_data.id}) successfully.")

@app.command()
def load(
    identifier: int = typer.Argument(help="Pokemon ID to load"),
    sample: bool = typer.Option(False, "--sample", help="Use sample data instead of API")
):
    """Load and insert Pokemon data by ID (use --sample for fallback)."""
    create_db_and_tables()
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
