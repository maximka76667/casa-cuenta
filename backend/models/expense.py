from pydantic import BaseModel
from typing import List


class ExpenseIn(BaseModel):
    group_id: str
    name: str
    amount: float
    payer_id: str


class ExpenseOut(BaseModel):
    id: str
    group_id: str
    name: str
    amount: float
    payer_id: str


class ExpenseUpdate(BaseModel):
    group_id: str | None = None
    title: str | None = None
    amount: float | None = None
    payer_id: str | None = None


class ExpenseCreate(BaseModel):
    name: str
    group_id: str
    payer_id: str
    amount: float
    debtors: List[str]


class ExpenseListResponse(BaseModel):
    expenses: List[ExpenseOut]
