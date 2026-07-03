from pydantic import BaseModel
from typing import List, Dict, Optional

class Card(BaseModel):
    id: str
    title: str
    details: str

class Column(BaseModel):
    id: str
    title: str
    cardIds: List[str]

class BoardData(BaseModel):
    columns: List[Column]
    cards: Dict[str, Card]
