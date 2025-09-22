import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.models import Pokemon, Type, PokemonType, PokemonStat, Sprite
from sqlmodel import SQLModel, create_engine, Session

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def test_db():
    engine_test = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine_test)
    with Session(engine_test) as session:
        # Insert test data for Bulbasaur
        pokemon = Pokemon(id=1, name="bulbasaur", height=7, weight=69)
        session.add(pokemon)
        session.flush()
        
        grass = Type(id=12, name="grass")
        poison = Type(id=4, name="poison")
        session.add(grass)
        session.add(poison)
        session.flush()
        
        pt1 = PokemonType(pokemon_id=1, type_id=12, slot=1)
        pt2 = PokemonType(pokemon_id=1, type_id=4, slot=2)
        session.add(pt1)
        session.add(pt2)
        
        stats = [
            PokemonStat(pokemon_id=1, stat_name="hp", base_stat=45),
            PokemonStat(pokemon_id=1, stat_name="attack", base_stat=49),
            # Add all 6
            PokemonStat(pokemon_id=1, stat_name="defense", base_stat=49),
            PokemonStat(pokemon_id=1, stat_name="special-attack", base_stat=65),
            PokemonStat(pokemon_id=1, stat_name="special-defense", base_stat=65),
            PokemonStat(pokemon_id=1, stat_name="speed", base_stat=45),
        ]
        for stat in stats:
            session.add(stat)
        
        sprites = [
            Sprite(pokemon_id=1, variant="front_default", url="https://default.png"),
            Sprite(pokemon_id=1, variant="front_shiny", url="https://shiny.png"),
            # No front_female
        ]
        for sprite in sprites:
            session.add(sprite)
        
        session.commit()
        yield session
    SQLModel.metadata.drop_all(engine_test)

def test_get_pokemon(test_client, test_db):
    response = test_client.get("/pokemon/1")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == 1
    assert data["name"] == "bulbasaur"
    assert data["height_m"] == 0.7
    assert data["weight_kg"] == 6.9
    assert len(data["types"]) == 2
    assert "grass" in [t["name"] for t in data["types"]]
    assert len(data["stats"]) == 6
    assert data["stats"][0]["base_stat"] == 45  # hp
    assert data["sprites"]["front_default"] == "https://default.png"
    assert data["sprites"]["front_female"] is None

def test_get_pokemon_not_found(test_client):
    response = test_client.get("/pokemon/999")
    assert response.status_code == 404

def test_get_sprite(test_client, test_db):
    response = test_client.get("/pokemon/1/sprites/front_default")
    data = response.json()
    assert response.status_code == 200
    assert data["url"] == "https://default.png"
    assert data["available"] is True

def test_get_sprite_missing(test_client, test_db):
    response = test_client.get("/pokemon/1/sprites/front_female")
    assert response.status_code == 404

def test_api_integration_joins(test_client, test_db):
    # Test full join query for Bulbasaur
    response = test_client.get("/pokemon/1")
    data = response.json()
    assert len(data["types"]) == 2
    assert "grass" in [t["name"] for t in data["types"]]
    assert "poison" in [t["name"] for t in data["types"]]
    assert len(data["stats"]) == 6
    assert data["stats"][0]["name"] == "hp" and data["stats"][0]["base_stat"] == 45
    assert data["sprites"]["front_female"] is None  # Null handling
    assert data["height_m"] == 0.7
    assert data["weight_kg"] == 6.9

def test_api_performance(test_client, test_db):
    import time
    start = time.time()
    response = test_client.get("/pokemon/1")
    end = time.time()
    assert end - start < 0.1  # <100ms
    assert response.status_code == 200

def test_post_search(test_client, test_db):
    response = test_client.post("/pokemon", data={"identifier": "1"})
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == 1
    assert len(data["types"]) == 2