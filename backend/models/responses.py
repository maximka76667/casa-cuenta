from typing import List, Dict, Any
from pydantic import BaseModel


class DebtorListResponse(BaseModel):
    debtors: List[Dict[str, Any]]


class PersonListResponse(BaseModel):
    persons: List[Dict[str, Any]]


class MemberListResponse(BaseModel):
    members: List[Dict[str, Any]]


class GroupListResponse(BaseModel):
    groups: List[Dict[str, Any]]


class GroupResponse(BaseModel):
    group: Dict[str, Any]


class GroupPersonsResponse(BaseModel):
    persons: List[Dict[str, Any]]


class GroupBalancesResponse(BaseModel):
    balances: Dict[str, Dict[str, Any]]


class UserGroupsResponse(BaseModel):
    groups: List[Dict[str, Any]]
