from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional
from src.models import Pokemon, Type, PokemonType, PokemonStat, Sprite, engine, Session as DBSession, select, create_db_and_tables
from src.schemas import PokemonResponse, SpriteResponse, TypeInfo, Stat
from sqlmodel import func  # Not used but for potential

def get_db():
    db = DBSession(engine)
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Pokedex API", description="Pokedex MVP API")

@app.on_event("startup")
def startup_event():
    create_db_and_tables()

# Mount UI
app.mount("/ui", StaticFiles(directory="public/ui"), name="ui")

@app.get("/")
def read_root():
    return {"message": "Pokedex API ready. Load Pokemon via /pokemon/{id}"}

@app.get("/pokemon/{identifier}", response_model=PokemonResponse)
def get_pokemon(identifier: str, db: DBSession = Depends(get_db)):
    try:
        id_int = int(identifier)
        query = select(Pokemon).where(Pokemon.id == id_int)
    except ValueError:
        query = select(Pokemon).where(Pokemon.name == identifier.lower())
    
    pokemon = db.exec(query.options(
        joinedload(Pokemon.types),
        joinedload(Pokemon.stats),
        joinedload(Pokemon.sprites)
    )).first()
    
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    
    # Build types
    types_list = [{"name": pt.type.name, "slot": pt.slot} for pt in pokemon.types]
    
    # Build stats
    stats_list = [{"name": ps.stat_name, "base_stat": ps.base_stat} for ps in pokemon.stats]
    
    # Build sprites dict, add None for missing
    sprites_dict = {s.variant: s.url for s in pokemon.sprites}
    expected_variants = ["front_default", "front_shiny", "back_default", "front_female"]
    for variant in expected_variants:
        if variant not in sprites_dict:
            sprites_dict[variant] = None
    
    response = PokemonResponse(
        id=pokemon.id,
        name=pokemon.name,
        height_m=pokemon.height / 10.0,
        weight_kg=pokemon.weight / 10.0,
        types=types_list,
        stats=stats_list,
        sprites=sprites_dict
    )
    return response

@app.get("/pokemon/{id}/sprites/{variant}", response_model=SpriteResponse)
def get_sprite(id: int, variant: str, db: DBSession = Depends(get_db)):
    sprite = db.exec(select(Sprite).where(Sprite.pokemon_id == id, Sprite.variant == variant)).first()  # type: ignore [attr-defined]
    if not sprite:
        raise HTTPException(status_code=404, detail="Sprite not found")
    return SpriteResponse(url=sprite.url, available=bool(sprite.url))

@app.post("/pokemon")
def search_pokemon(identifier: str = Form(...), db: DBSession = Depends(get_db)):
    # Reuse get_pokemon logic, return JSON
    try:
        id_int = int(identifier)
        query = select(Pokemon).where(Pokemon.id == id_int)
    except ValueError:
        query = select(Pokemon).where(Pokemon.name == identifier.lower())
    
    pokemon = db.exec(query.options(
        joinedload(Pokemon.types),
        joinedload(Pokemon.stats),
        joinedload(Pokemon.sprites)
    )).first()
    
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    
    # Same as above
    types_list = [{"name": pt.type.name, "slot": pt.slot} for pt in pokemon.types]
    stats_list = [{"name": ps.stat_name, "base_stat": ps.base_stat} for ps in pokemon.stats]
    sprites_dict = {s.variant: s.url for s in pokemon.sprites}
    for v in ["front_default", "front_shiny", "back_default", "front_female"]:
        if v not in sprites_dict:
            sprites_dict[v] = None
    
    return {
        "id": pokemon.id,
        "name": pokemon.name,
        "height_m": pokemon.height / 10.0,
        "weight_kg": pokemon.weight / 10.0,
        "types": types_list,
        "stats": stats_list,
        "sprites": sprites_dict
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)