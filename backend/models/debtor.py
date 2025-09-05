from typing import Any, Dict, List
from pydantic import BaseModel


class ExpenseDebtorIn(BaseModel):
    expense_id: str
    person_id: str


class ExpenseDebtorUpdate(BaseModel):
    expense_id: str | None = None
    person_id: str | None = None


class DebtorListResponse(BaseModel):
    debtors: List[Dict[str, Any]]
