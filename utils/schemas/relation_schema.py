from pydantic import BaseModel
from enum import Enum
from typing import List

class Polarity(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"

class Relation(BaseModel):
    object1: str
    object2: str
    relation_type: str
    polarity: Polarity
    keywords: List[str]

class RelationList(BaseModel):
    relations: List[Relation]
