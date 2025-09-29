from pydantic import BaseModel
from typing import List, Union


class ExpenseOut(BaseModel):
    id: str
    group_id: str
    name: str
    amount: float
    payer_id: str


class ExpenseUpdate(BaseModel):
    group_id: str | None = None
    name: str | None = None
    amount: float | None = None
    payer_id: str | None = None


class DebtorWithValue(BaseModel):
    id: str
    value: float


class ExpenseCreate(BaseModel):
    name: str
    group_id: str
    payer_id: str
    amount: float
    debtors: Union[List[str], List[DebtorWithValue]]
    split_type: str


class ExpenseListResponse(BaseModel):
    expenses: List[dict]
