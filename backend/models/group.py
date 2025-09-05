from typing import Any, Dict, List
from pydantic import BaseModel


class GroupIn(BaseModel):
    name: str


class GroupUpdate(BaseModel):
    name: str | None = None


class GroupListResponse(BaseModel):
    groups: List[Dict[str, Any]]


class GroupResponse(BaseModel):
    group: Dict[str, Any]


class GroupPersonsResponse(BaseModel):
    persons: List[Dict[str, Any]]


class GroupBalancesResponse(BaseModel):
    balances: Dict[str, Dict[str, Any]]
