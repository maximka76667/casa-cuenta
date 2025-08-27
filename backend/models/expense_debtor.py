from pydantic import BaseModel

class ExpenseDebtorIn(BaseModel):
    expense_id: str
    person_id: str
    amount: float

class ExpenseDebtorUpdate(BaseModel):
    expense_id: str | None = None
    person_id: str | None = None
    amount: float | None = None