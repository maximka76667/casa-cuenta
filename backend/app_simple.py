import uuid
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Data Models
class PersonIn(BaseModel):
    name: str
    group_id: str

class PersonOut(BaseModel):
    id: str
    name: str
    group_id: str
    created_at: str

class GroupIn(BaseModel):
    name: str

class GroupOut(BaseModel):
    id: str
    name: str
    created_at: str

class ExpenseIn(BaseModel):
    name: str
    amount: float
    payer_id: str
    group_id: str
    debtors: List[str]

class ExpenseOut(BaseModel):
    id: str
    name: str
    amount: float
    payer_id: str
    group_id: str
    created_at: str

class ExpenseDebtorOut(BaseModel):
    id: str
    expense_id: str
    person_id: str
    amount: float

# In-memory storage
groups: Dict[str, GroupOut] = {}
persons: Dict[str, PersonOut] = {}
expenses: Dict[str, ExpenseOut] = {}
expense_debtors: Dict[str, ExpenseDebtorOut] = {}

app = FastAPI()

# CORS setup - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def hello():
    return {"message": "Casa Cuenta - Simple Expense Tracker"}

# Groups
@app.post("/groups", response_model=GroupOut)
def create_group(group: GroupIn):
    group_id = str(uuid.uuid4())
    new_group = GroupOut(
        id=group_id,
        name=group.name,
        created_at=datetime.now().isoformat()
    )
    groups[group_id] = new_group
    return new_group

@app.get("/groups/{group_id}", response_model=GroupOut)
def get_group(group_id: str):
    if group_id not in groups:
        raise HTTPException(status_code=404, detail="Group not found")
    return groups[group_id]

@app.get("/groups", response_model=List[GroupOut])
def get_all_groups():
    return list(groups.values())

# Persons
@app.post("/persons", response_model=PersonOut)
def add_person(person: PersonIn):
    # Verify group exists
    if person.group_id not in groups:
        raise HTTPException(status_code=404, detail="Group not found")
    
    person_id = str(uuid.uuid4())
    new_person = PersonOut(
        id=person_id,
        name=person.name,
        group_id=person.group_id,
        created_at=datetime.now().isoformat()
    )
    persons[person_id] = new_person
    return new_person

@app.get("/groups/{group_id}/persons", response_model=List[PersonOut])
def get_group_persons(group_id: str):
    if group_id not in groups:
        raise HTTPException(status_code=404, detail="Group not found")
    
    group_persons = [person for person in persons.values() if person.group_id == group_id]
    return group_persons

@app.delete("/persons/{person_id}")
def delete_person(person_id: str):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    
    deleted_person = persons.pop(person_id)
    return {"message": "Person deleted", "deleted_person": deleted_person}

# Expenses
@app.post("/expenses", response_model=ExpenseOut)
def add_expense(expense: ExpenseIn):
    # Verify group and payer exist
    if expense.group_id not in groups:
        raise HTTPException(status_code=404, detail="Group not found")
    if expense.payer_id not in persons:
        raise HTTPException(status_code=404, detail="Payer not found")
    
    # Verify all debtors exist
    for debtor_id in expense.debtors:
        if debtor_id not in persons:
            raise HTTPException(status_code=404, detail=f"Debtor {debtor_id} not found")
    
    expense_id = str(uuid.uuid4())
    new_expense = ExpenseOut(
        id=expense_id,
        name=expense.name,
        amount=expense.amount,
        payer_id=expense.payer_id,
        group_id=expense.group_id,
        created_at=datetime.now().isoformat()
    )
    expenses[expense_id] = new_expense
    
    # Create expense debtors (split equally)
    share_amount = expense.amount / len(expense.debtors)
    for debtor_id in expense.debtors:
        debtor_expense_id = str(uuid.uuid4())
        expense_debtor = ExpenseDebtorOut(
            id=debtor_expense_id,
            expense_id=expense_id,
            person_id=debtor_id,
            amount=share_amount
        )
        expense_debtors[debtor_expense_id] = expense_debtor
    
    return new_expense

@app.get("/expenses/{group_id}", response_model=List[ExpenseOut])
def get_expenses_for_group(group_id: str):
    if group_id not in groups:
        raise HTTPException(status_code=404, detail="Group not found")
    
    group_expenses = [expense for expense in expenses.values() if expense.group_id == group_id]
    return group_expenses

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str):
    if expense_id not in expenses:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Delete expense and related debtors
    deleted_expense = expenses.pop(expense_id)
    
    # Remove related expense debtors
    debtors_to_remove = [debtor_id for debtor_id, debtor in expense_debtors.items() 
                        if debtor.expense_id == expense_id]
    for debtor_id in debtors_to_remove:
        expense_debtors.pop(debtor_id)
    
    return {"message": "Expense deleted", "deleted_expense": deleted_expense}

# Expense Debtors
@app.get("/debtors/{group_id}", response_model=List[ExpenseDebtorOut])
def get_debtors_for_group(group_id: str):
    if group_id not in groups:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Get all expenses for the group
    group_expense_ids = [expense.id for expense in expenses.values() if expense.group_id == group_id]
    
    # Get all debtors for those expenses
    group_debtors = [debtor for debtor in expense_debtors.values() 
                    if debtor.expense_id in group_expense_ids]
    
    return group_debtors

# Balance calculation endpoint
@app.get("/groups/{group_id}/balances")
def get_group_balances(group_id: str):
    if group_id not in groups:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Get all persons in the group
    group_persons = [person for person in persons.values() if person.group_id == group_id]
    
    # Initialize balances
    balances = {person.id: {"name": person.name, "paid": 0.0, "owes": 0.0, "balance": 0.0} 
               for person in group_persons}
    
    # Calculate what each person paid
    group_expenses = [expense for expense in expenses.values() if expense.group_id == group_id]
    for expense in group_expenses:
        if expense.payer_id in balances:
            balances[expense.payer_id]["paid"] += expense.amount
    
    # Calculate what each person owes
    group_expense_ids = [expense.id for expense in group_expenses]
    group_debtors = [debtor for debtor in expense_debtors.values() 
                    if debtor.expense_id in group_expense_ids]
    
    for debtor in group_debtors:
        if debtor.person_id in balances:
            balances[debtor.person_id]["owes"] += debtor.amount
    
    # Calculate net balance (positive means they are owed money, negative means they owe money)
    for person_id in balances:
        balances[person_id]["balance"] = balances[person_id]["paid"] - balances[person_id]["owes"]
    
    return {"balances": balances}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)