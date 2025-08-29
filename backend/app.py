import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt
import httpx
from dotenv import load_dotenv
from supabase import create_client
from fastapi.middleware.cors import CORSMiddleware

from models.auth import AuthCredentials
from models.person import PersonIn, PersonUpdate
from models.expense import (
    ExpenseIn,
    ExpenseUpdate,
    ExpenseCreate,
    ExpenseOut,
    ExpenseListResponse,
)
from models.group import GroupIn, GroupUpdate
from models.group_user import GroupUserIn, GroupUserUpdate
from models.expense_debtor import ExpenseDebtorIn, ExpenseDebtorUpdate

import redis.asyncio as redis

load_dotenv()

app = FastAPI()
security = HTTPBearer()


SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")
SUPABASE_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co"
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)

# jwks_cache = None

# async def get_jwks():
#     global jwks_cache
#     if jwks_cache is None:
#         async with httpx.AsyncClient() as client:
#             resp = await client.get(SUPABASE_JWKS_URL)
#             resp.raise_for_status()
#             jwks_cache = resp.json()
#     return jwks_cache

# async def verify_jwt(credentials=Depends(security)):
#     token = credentials.credentials
#     jwks = await get_jwks()

#     try:
#         payload = jwt.decode(
#             token,
#             jwks,
#             algorithms=["RS256"],
#             audience=f"https://{SUPABASE_PROJECT_ID}.supabase.co/auth/v1"
#         )
#         return payload
#     except Exception:
#         raise HTTPException(status_code=401, detail="Invalid token")

origins = [
    "http://localhost:5173",
    "http://localhost:12000",
    "http://localhost:12001",
    "http://localhost:12006",
    "http://localhost:12007",
    "https://work-1-azccrmdytbbrmuij.prod-runtime.all-hands.dev",
]

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_redis():
    client = redis.Redis.from_pool(redis_pool)
    try:
        yield client
    finally:
        await client.aclose()


@app.get("/")
async def hello():
    return {"message": "Hello!"}


# Auth
@app.post("/signup")
def signup(auth: AuthCredentials):
    user = supabase.auth.sign_up(
        {"email": auth.email, "password": auth.password, "email_confirm": False}
    )
    return {"user": user}


@app.post("/signin")
def signin(auth: AuthCredentials):
    response = supabase.auth.sign_in_with_password(
        {
            "email": auth.email,
            "password": auth.password,
        }
    )
    return {"user": response.user, "access_token": response.session.access_token}


# Expenses
@app.get("/expenses")
def get_expenses():
    response = supabase.table("expenses").select("*").execute()

    return {"expenses": response.data}


@app.get("/expenses/{group_id}")
async def get_expenses_for_group(
    group_id: str, redis_client: redis.Redis = Depends(get_redis)
):
    cache_key = f"expenses:group:{group_id}"
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        # If found in cache, return it parsed from JSON (super fast!)
        print("Cache (Expenses): Returning from Redis.")
        return ExpenseListResponse.model_validate_json(cached_data)

    # If not found in cache -> fetch from db
    response = supabase.table("expenses").select("*").eq("group_id", group_id).execute()

    expenses_list = response.data
    response_data = ExpenseListResponse(expenses=expenses_list)

    await redis_client.setex(cache_key, 30, response_data.model_dump_json())

    return response_data


@app.post("/expenses")
def add_expense(expense: ExpenseCreate):

    new_expense = {
        "name": expense.name,
        "amount": expense.amount,
        "payer_id": expense.payer_id,
        "group_id": expense.group_id,
    }
    expense_response = supabase.table("expenses").insert(new_expense).execute()

    # Get inserted expense id
    expense_id = expense_response.data[0]["id"]

    # Share expense amount equally between debtors
    share_amount = expense.amount / len(expense.debtors)

    debtors_data = [
        {"expense_id": expense_id, "person_id": debtor_id, "amount": share_amount}
        for debtor_id in expense.debtors
    ]

    response = supabase.table("expenses_debtors").insert(debtors_data).execute()

    return {
        "message": "Expense added",
        "expense": expense_response.data[0],
        "debtors": response.data,
    }


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str):
    response = supabase.table("expenses").delete().eq("id", expense_id).execute()
    return {"message": "Expense deleted", "deleted_expense": response.data}


@app.put("/expenses/{expense_id}")
def update_expense(expense_id: str, expense: ExpenseUpdate):
    response = (
        supabase.table("expenses")
        .update(expense.model_dump())
        .eq("id", expense_id)
        .execute()
    )
    return {"message": "Expense updated", "expense": response.data}


# Expense Debtors
@app.get("/debtors")
def get_debtors():
    response = supabase.table("expenses_debtors").select("*").execute()

    return {"debtors": response.data}


@app.get("/debtors/{group_id}")
def get_debtors_for_group(group_id: str):
    response = (
        supabase.from_("expenses_debtors")
        .select("*, expenses(group_id)")
        .eq("expenses.group_id", group_id)
        .execute()
    )

    return {"debtors": response.data}


@app.post("/debtors")
def add_debtor(debtor: ExpenseDebtorIn):
    response = supabase.table("expenses_debtors").insert(debtor.model_dump()).execute()
    return {"message": "Debtor added", "debtor": response.data}


@app.delete("/debtors/{debtor_id}")
def delete_debtor(debtor_id: str):
    response = supabase.table("expenses_debtors").delete().eq("id", debtor_id).execute()
    return {"message": "Debtor deleted", "deleted_debtor": response.data}


@app.put("/debtors/{debtor_id}")
def update_debtor(debtor_id: str, debtor: ExpenseDebtorUpdate):
    response = (
        supabase.table("expenses_debtors")
        .update(debtor.model_dump())
        .eq("id", debtor_id)
        .execute()
    )
    return {"message": "Debtor updated", "debtor": response.data}


# Persons
@app.get("/persons")
def get_persons():
    response = supabase.table("persons").select("*").execute()

    return {"persons": response.data}


@app.post("/persons")
def add_person(person: PersonIn):
    try:
        response = supabase.table("persons").insert(person.model_dump()).execute()
    except:
        raise HTTPException(500, "Error on adding person")
    return {"message": "Person added", "person": response.data}


@app.delete("/persons/{person_id}")
def delete_person(person_id: str):
    try:
        response = supabase.table("persons").delete().eq("id", person_id).execute()
    except:
        raise HTTPException(500, "Error on deleting person")
    return {"message": "Persone deleted", "deleted_person": response.data}


@app.put("/persons/{person_id}")
def update_person(person_id: str, person: PersonUpdate):
    response = (
        supabase.table("persons")
        .update(person.model_dump())
        .eq("id", person_id)
        .execute()
    )
    return {"message": "Person updated", "person": response.data}


# Group Users
@app.get("/members")
def get_members():
    response = supabase.table("group_users").select("*").execute()

    return {"members": response.data}


@app.post("/members")
def add_member(member: GroupUserIn):
    response = supabase.table("group_users").insert(member.model_dump()).execute()
    return {"message": "Member added", "member": response.data}


@app.delete("/members/{member_id}")
def delete_member(member_id: str):
    response = supabase.table("group_users").delete().eq("id", member_id).execute()
    return {"message": "Member deleted", "deleted_member": response.data}


@app.put("/members/{member_id}")
def update_member(member_id: str, member: GroupUserUpdate):
    response = (
        supabase.table("group_users")
        .update(member.model_dump())
        .eq("id", member_id)
        .execute()
    )
    return {"message": "Member updated", "member": response.data}


# Groups
@app.get("/groups")
def get_groups():
    response = supabase.table("groups").select("*").execute()
    return {"groups": response.data}


@app.get("/groups/{group_id}")
def get_group(group_id: str):
    response = (
        supabase.table("groups").select("*").eq("id", group_id).single().execute()
    )
    return {"group": response.data}


@app.get("/groups/{group_id}/persons")
def get_group_persons(group_id: str):
    response = supabase.table("persons").select("*").eq("group_id", group_id).execute()

    return {"persons": response.data}


@app.post("/groups")
def add_group(group: GroupIn):
    response = supabase.table("groups").insert(group.model_dump()).execute()
    return {"message": "Group added", "group": response.data}


@app.delete("/groups/{group_id}")
def delete_group(group_id: str):
    response = supabase.table("groups").delete().eq("id", group_id).execute()
    return {"message": "Group deleted", "deleted_group": response.data}


@app.put("/groups/{group_id}")
def update_group(group_id: str, group: GroupUpdate):
    response = (
        supabase.table("groups").update(group.model_dump()).eq("id", group_id).execute()
    )
    return {"message": "Group updated", "group": response.data}


@app.get("/groups/{group_id}/balances")
def get_group_balances(group_id: str):
    # 1. Verify group exists
    group = supabase.table("groups").select("id").eq("id", group_id).single().execute()
    if not group.data:
        raise HTTPException(status_code=404, detail="Group not found")

    # 2. Get persons in group
    persons = (
        supabase.table("persons")
        .select("id, name")
        .eq("group_id", group_id)
        .execute()
        .data
    )
    if not persons:
        return {"balances": {}}

    balances = {
        person["id"]: {
            "name": person["name"],
            "paid": 0.0,
            "owes": 0.0,
            "balance": 0.0,
        }
        for person in persons
    }

    # 3. Get all expenses for this group
    expenses = (
        supabase.table("expenses")
        .select("id, amount, payer_id")
        .eq("group_id", group_id)
        .execute()
        .data
    )
    expense_ids = [e["id"] for e in expenses]

    # 4. Aggregate "paid" by payer
    for e in expenses:
        payer_id = e["payer_id"]
        if payer_id in balances:
            balances[payer_id]["paid"] += float(e["amount"])

    # 5. Get debtors only for this group's expenses
    if expense_ids:
        debtors = (
            supabase.table("expenses_debtors")
            .select("person_id, amount, expense_id")
            .in_("expense_id", expense_ids)
            .execute()
            .data
        )

        for d in debtors:
            if d["person_id"] in balances:
                balances[d["person_id"]]["owes"] += float(d["amount"])

    # 6. Compute net balance
    for person_id, data in balances.items():
        data["balance"] = data["paid"] - data["owes"]

    return {"balances": balances}


# Users
@app.get("/users/{user_id}/groups")
def get_user_groups(user_id: str):
    response = (
        supabase.table("group_users")
        .select("group:groups(id, name, created_at)")  # Fetch full group data
        .eq("user_id", user_id)
        .execute()
    )

    return {"groups": [g["group"] for g in response.data]}
