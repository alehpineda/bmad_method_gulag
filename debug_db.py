from src.models import Pokemon, engine, Session, select

with Session(engine) as session:
    result = session.exec(select(Pokemon).where(Pokemon.id == 1)).first()
    if result:
        print(f"Result object: {result}")
        print(f"Result type: {type(result)}")
        # Try accessing first element if it's a row/tuple
        if hasattr(result, '__iter__') and not isinstance(result, str):
            pokemon = result[0] if len(result) > 0 else result
        else:
            pokemon = result
        print(f"Pokemon object: {pokemon}")
        print(f"Pokemon type: {type(pokemon)}")
        print(f"Pokemon id: {pokemon.id}")
        print(f"Pokemon name: {pokemon.name}")
    else:
        print("No pokemon found")
