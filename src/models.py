from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, create_engine
from sqlalchemy import Column, Integer

class Pokemon(SQLModel, table=True):
    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=False))
    name: str = Field(index=True)
    height: int  # decimeters
    weight: int  # hectograms
    
    # Relationships
    types: List["PokemonType"] = Relationship(back_populates="pokemon")
    stats: List["PokemonStat"] = Relationship(back_populates="pokemon")
    sprites: List["Sprite"] = Relationship(back_populates="pokemon")

class Type(SQLModel, table=True):
    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True, autoincrement=True))
    name: str = Field(index=True, unique=True)
    
    # Relationship
    pokemon_types: List["PokemonType"] = Relationship(back_populates="type")

class PokemonType(SQLModel, table=True):
    pokemon_id: int = Field(foreign_key="pokemon.id", primary_key=True)
    type_id: int = Field(foreign_key="type.id", primary_key=True)
    slot: int
    
    # Relationships
    pokemon: Pokemon = Relationship(back_populates="types")
    type: Type = Relationship(back_populates="pokemon_types")

class PokemonStat(SQLModel, table=True):
    pokemon_id: int = Field(foreign_key="pokemon.id", primary_key=True)
    stat_name: str = Field(primary_key=True)
    base_stat: int
    
    # Relationship
    pokemon: Pokemon = Relationship(back_populates="stats")

class Sprite(SQLModel, table=True):
    pokemon_id: int = Field(foreign_key="pokemon.id", primary_key=True)
    variant: str = Field(primary_key=True)
    url: str
    
    # Relationship
    pokemon: Pokemon = Relationship(back_populates="sprites")

# Database setup
engine = create_engine("sqlite:///pokedex.db", echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)