from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from src.models import Pokemon, Type, PokemonType, PokemonStat, Sprite, engine, create_db_and_tables
from src.schemas import PokemonResponse, SpriteResponse, TypeInfo, Stat
from sqlmodel import Session, select

def extract_model(result):
    """Extract SQLModel object from SQLAlchemy Row if needed"""
    if result is None:
        return None
    return result[0] if hasattr(result, '__iter__') and not isinstance(result, str) else result

def get_db():
    db = Session(engine)
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
def get_pokemon(identifier: str, db: Session = Depends(get_db)):
    try:
        id_int = int(identifier)
        query = select(Pokemon).where(Pokemon.id == id_int)
    except ValueError:
        query = select(Pokemon).where(Pokemon.name == identifier.lower())
    
    result = db.exec(query).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    
    # Extract Pokemon object from Row
    pokemon = extract_model(result)
    
    # Build types by querying separately
    pokemon_types_result = db.exec(select(PokemonType).where(PokemonType.pokemon_id == pokemon.id)).all()
    types_list = []
    for pt_row in pokemon_types_result:
        pt = extract_model(pt_row)
        type_result = db.exec(select(Type).where(Type.id == pt.type_id)).first()
        if type_result:
            type_obj = extract_model(type_result)
            types_list.append(TypeInfo(name=type_obj.name, slot=pt.slot))
    
    # Build stats
    stats_list = []
    pokemon_stats_result = db.exec(select(PokemonStat).where(PokemonStat.pokemon_id == pokemon.id)).all()
    for ps_row in pokemon_stats_result:
        ps = extract_model(ps_row)
        stats_list.append(Stat(name=ps.stat_name, base_stat=ps.base_stat))
    
    # Build sprites dict, add None for missing
    sprites_result = db.exec(select(Sprite).where(Sprite.pokemon_id == pokemon.id)).all()
    sprites_dict = {}
    for s_row in sprites_result:
        s = extract_model(s_row)
        sprites_dict[s.variant] = s.url
    
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
def get_sprite(id: int, variant: str, db: Session = Depends(get_db)):
    result = db.exec(select(Sprite).where(Sprite.pokemon_id == id, Sprite.variant == variant)).first()  # type: ignore [attr-defined]
    if not result:
        raise HTTPException(status_code=404, detail="Sprite not found")
    sprite = extract_model(result)
    return SpriteResponse(url=sprite.url, available=bool(sprite.url))

@app.post("/pokemon")
def search_pokemon(identifier: str = Form(...), db: Session = Depends(get_db)):
    # Reuse get_pokemon logic, return JSON
    try:
        id_int = int(identifier)
        query = select(Pokemon).where(Pokemon.id == id_int)
    except ValueError:
        query = select(Pokemon).where(Pokemon.name == identifier.lower())
    
    result = db.exec(query).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    
    # Extract Pokemon object from Row
    pokemon = extract_model(result)
    
    # Build types by querying separately
    pokemon_types_result = db.exec(select(PokemonType).where(PokemonType.pokemon_id == pokemon.id)).all()
    types_list = []
    for pt_row in pokemon_types_result:
        pt = extract_model(pt_row)
        type_result = db.exec(select(Type).where(Type.id == pt.type_id)).first()
        if type_result:
            type_obj = extract_model(type_result)
            types_list.append({"name": type_obj.name, "slot": pt.slot})
    
    # Build stats
    stats_list = []
    pokemon_stats_result = db.exec(select(PokemonStat).where(PokemonStat.pokemon_id == pokemon.id)).all()
    for ps_row in pokemon_stats_result:
        ps = extract_model(ps_row)
        stats_list.append({"name": ps.stat_name, "base_stat": ps.base_stat})
    
    # Build sprites dict, add None for missing
    sprites_result = db.exec(select(Sprite).where(Sprite.pokemon_id == pokemon.id)).all()
    sprites_dict = {}
    for s_row in sprites_result:
        s = extract_model(s_row)
        sprites_dict[s.variant] = s.url
    
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