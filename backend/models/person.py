from typing import Any, Dict, List
from pydantic import BaseModel


class PersonIn(BaseModel):
    name: str
    user_id: str | None = None
    group_id: str


class PersonUpdate(BaseModel):
    name: str | None = None
    user_id: str | None = None
    group_id: str | None = None


class PersonListResponse(BaseModel):
    persons: List[Dict[str, Any]]
