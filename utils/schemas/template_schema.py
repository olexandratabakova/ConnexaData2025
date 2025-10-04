from pydantic import BaseModel
from typing import List

class Topics(BaseModel):
    entities_of_interest: List[str]
    relation_types: List[str]
    keywords: List[str]

class Tips(BaseModel):
    tips: List[Topics]

