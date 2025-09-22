from pydantic import BaseModel
from typing import List, Optional, Dict

class Stat(BaseModel):
    name: str
    base_stat: int

class TypeInfo(BaseModel):
    name: str
    slot: int

class SpriteResponse(BaseModel):
    url: Optional[str]
    available: bool

class PokemonResponse(BaseModel):
    id: int
    name: str
    height_m: float
    weight_kg: float
    types: List[TypeInfo]
    stats: List[Stat]
    sprites: Dict[str, Optional[str]]

class PokemonData(BaseModel):
    id: int
    name: str
    height: int
    weight: int
    types: List[dict]  # {"slot": int, "type_name": str}
    stats: List[dict]  # {"stat_name": str, "base_stat": int}
    sprites: Dict[str, str]