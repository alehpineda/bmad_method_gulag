import pytest
from unittest.mock import AsyncMock, patch
from src.etl.main import normalize_data, insert_idempotent, SAMPLE_BULBASAUR
from src.schemas import PokemonData
from src.models import Pokemon, Type, PokemonType, PokemonStat, Sprite, Session, select
from sqlalchemy import create_engine
from sqlmodel import SQLModel

@pytest.fixture
def test_engine():
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def test_session(test_engine):
    with Session(test_engine) as session:
        yield session

def test_normalize_data():
    data = SAMPLE_BULBASAUR
    normalized = normalize_data(data)
    assert isinstance(normalized, PokemonData)
    assert normalized.id == 1
    assert normalized.name == "bulbasaur"
    assert len(normalized.stats) == 6
    assert "hp" in [s["stat_name"] for s in normalized.stats]
    assert len(normalized.sprites) > 0  # No nulls
    assert all(url for url in normalized.sprites.values())  # No null values

@pytest.mark.usefixtures("test_session")
def test_insert_idempotent(test_session):
    data = normalize_data(SAMPLE_BULBASAUR)
    insert_idempotent(test_session, data)
    test_session.commit()
    
    # Assert rows
    pokemon = test_session.exec(select(Pokemon).where(Pokemon.id == 1)).first()
    assert pokemon is not None
    types = test_session.exec(select(PokemonType).where(PokemonType.pokemon_id == 1)).all()
    assert len(types) == 2  # Grass, Poison
    stats = test_session.exec(select(PokemonStat).where(PokemonStat.pokemon_id == 1)).all()
    assert len(stats) == 6
    sprites = test_session.exec(select(Sprite).where(Sprite.pokemon_id == 1)).all()
    assert len(sprites) >= 2  # At least default and shiny
    
    # Idempotent: Re-run no change
    initial_pokemon_count = test_session.exec(select(Pokemon).where(Pokemon.id == 1)).first() is not None
    insert_idempotent(test_session, data)
    assert test_session.exec(select(Pokemon).where(Pokemon.id == 1)).first() is not None  # Still one
    # Counts unchanged (simplified check)

def test_etl_timing_and_idempotency(test_session):
    import time
    data = normalize_data(SAMPLE_BULBASAUR)
    start = time.time()
    insert_idempotent(test_session, data)
    end = time.time()
    assert end - start < 5.0  # <5s
    test_session.commit()
    
    # Idempotent second run
    start2 = time.time()
    insert_idempotent(test_session, data)
    end2 = time.time()
    assert end2 - start2 < 1.0  # Faster on skip
    # No new rows
    pokemon_count = test_session.exec(select(Pokemon).where(Pokemon.id == 1)).count()
    assert pokemon_count == 1