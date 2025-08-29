import os
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer
from jose import jwt
import httpx
from dotenv import load_dotenv
from supabase import create_client
from fastapi.middleware.cors import CORSMiddleware

import redis.asyncio as redis
import json

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
from models.responses import (
    DebtorListResponse,
    PersonListResponse,
    MemberListResponse,
    GroupListResponse,
    GroupResponse,
    GroupPersonsResponse,
    GroupBalancesResponse,
    UserGroupsResponse,
)

from routers import expenses

load_dotenv()


app = FastAPI()
security = HTTPBearer()


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


# async def invalidate_group_cache(redis_client: redis.Redis, group_id: str):
#     """Invalidate all cache keys related to a group"""
#     keys_to_delete = [
#         f"expenses:group:{group_id}",
#         f"debtors:group:{group_id}",
#         f"persons:group:{group_id}",
#         f"balances:group:{group_id}",
#         f"group:{group_id}",
#     ]
#     await redis_client.delete(*keys_to_delete)


# async def invalidate_global_cache(redis_client: redis.Redis, entity_type: str):
#     """Invalidate global cache keys for an entity type"""
#     keys_to_delete = [f"{entity_type}:all"]
#     await redis_client.delete(*keys_to_delete)


# async def invalidate_user_cache(redis_client: redis.Redis, user_id: str):
#     """Invalidate user-specific cache keys"""
#     keys_to_delete = [f"user:groups:{user_id}"]
#     await redis_client.delete(*keys_to_delete)


async def set_cache(data, key: str):
    await r.set(
        key,
        json.dumps(data),
        ex=30,
    )


async def get_cache(key: str):
    current_data = await r.get(key)

    if current_data:
        print(f"Data not found, fetching last data and storing into cache key {key}")
        return json.loads(current_data)
    print(f"Restoring cache for cache key {key}")


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


app.include_router(expenses.router)

# # Expense Debtors
# @app.get("/debtors")
# async def get_debtors(redis_client: redis.Redis = Depends(get_redis)):
#     cache_key = "debtors:all"
#     cached_data = await redis_client.get(cache_key)

#     if cached_data:
#         print("Cache (All Debtors): Returning from Redis.")
#         return DebtorListResponse.model_validate_json(cached_data)

#     response = supabase.table("expenses_debtors").select("*").execute()
#     response_data = DebtorListResponse(debtors=response.data)

#     await redis_client.setex(cache_key, 30, response_data.model_dump_json())

#     return response_data


# @app.get("/debtors/{group_id}")
# async def get_debtors_for_group(
#     group_id: str, redis_client: redis.Redis = Depends(get_redis)
# ):
#     cache_key = f"debtors:group:{group_id}"
#     cached_data = await redis_client.get(cache_key)

#     if cached_data:
#         print("Cache (Group Debtors): Returning from Redis.")
#         return DebtorListResponse.model_validate_json(cached_data)

#     response = (
#         supabase.from_("expenses_debtors")
#         .select("*, expenses(group_id)")
#         .eq("expenses.group_id", group_id)
#         .execute()
#     )

#     response_data = DebtorListResponse(debtors=response.data)

#     await redis_client.setex(cache_key, 30, response_data.model_dump_json())

#     return response_data


# @app.post("/debtors")
# async def add_debtor(
#     debtor: ExpenseDebtorIn, redis_client: redis.Redis = Depends(get_redis)
# ):
#     response = supabase.table("expenses_debtors").insert(debtor.model_dump()).execute()

#     expense_data = (
#         supabase.table("expenses")
#         .select("group_id")
#         .eq("id", debtor.expense_id)
#         .execute()
#     )
#     group_id = expense_data.data[0]["group_id"] if expense_data.data else None

#     await invalidate_global_cache(redis_client, "debtors")
#     if group_id:
#         await invalidate_group_cache(redis_client, group_id)

#     return {"message": "Debtor added", "debtor": response.data}


# @app.delete("/debtors/{debtor_id}")
# async def delete_debtor(debtor_id: str, redis_client: redis.Redis = Depends(get_redis)):
#     debtor_data = (
#         supabase.table("expenses_debtors")
#         .select("expense_id")
#         .eq("id", debtor_id)
#         .execute()
#     )
#     expense_id = debtor_data.data[0]["expense_id"] if debtor_data.data else None

#     group_id = None
#     if expense_id:
#         expense_data = (
#             supabase.table("expenses").select("group_id").eq("id", expense_id).execute()
#         )
#         group_id = expense_data.data[0]["group_id"] if expense_data.data else None

#     response = supabase.table("expenses_debtors").delete().eq("id", debtor_id).execute()

#     await invalidate_global_cache(redis_client, "debtors")
#     if group_id:
#         await invalidate_group_cache(redis_client, group_id)

#     return {"message": "Debtor deleted", "deleted_debtor": response.data}


# @app.put("/debtors/{debtor_id}")
# async def update_debtor(
#     debtor_id: str,
#     debtor: ExpenseDebtorUpdate,
#     redis_client: redis.Redis = Depends(get_redis),
# ):
#     debtor_data = (
#         supabase.table("expenses_debtors")
#         .select("expense_id")
#         .eq("id", debtor_id)
#         .execute()
#     )
#     expense_id = debtor_data.data[0]["expense_id"] if debtor_data.data else None

#     group_id = None
#     if expense_id:
#         expense_data = (
#             supabase.table("expenses").select("group_id").eq("id", expense_id).execute()
#         )
#         group_id = expense_data.data[0]["group_id"] if expense_data.data else None

#     response = (
#         supabase.table("expenses_debtors")
#         .update(debtor.model_dump())
#         .eq("id", debtor_id)
#         .execute()
#     )

#     await invalidate_global_cache(redis_client, "debtors")
#     if group_id:
#         await invalidate_group_cache(redis_client, group_id)

#     return {"message": "Debtor updated", "debtor": response.data}


# # Persons
# @app.get("/persons")
# async def get_persons(redis_client: redis.Redis = Depends(get_redis)):
#     cache_key = "persons:all"
#     cached_data = await redis_client.get(cache_key)

#     if cached_data:
#         print("Cache (All Persons): Returning from Redis.")
#         return PersonListResponse.model_validate_json(cached_data)

#     response = supabase.table("persons").select("*").execute()
#     response_data = PersonListResponse(persons=response.data)

#     await redis_client.setex(cache_key, 30, response_data.model_dump_json())

#     return response_data


# @app.post("/persons")
# async def add_person(person: PersonIn, redis_client: redis.Redis = Depends(get_redis)):
#     try:
#         response = supabase.table("persons").insert(person.model_dump()).execute()
#     except:
#         raise HTTPException(500, "Error on adding person")

#     await invalidate_global_cache(redis_client, "persons")
#     await invalidate_group_cache(redis_client, person.group_id)

#     return {"message": "Person added", "person": response.data}


# @app.delete("/persons/{person_id}")
# async def delete_person(person_id: str, redis_client: redis.Redis = Depends(get_redis)):
#     person_data = (
#         supabase.table("persons").select("group_id").eq("id", person_id).execute()
#     )
#     group_id = person_data.data[0]["group_id"] if person_data.data else None

#     try:
#         response = supabase.table("persons").delete().eq("id", person_id).execute()
#     except:
#         raise HTTPException(500, "Error on deleting person")

#     await invalidate_global_cache(redis_client, "persons")
#     if group_id:
#         await invalidate_group_cache(redis_client, group_id)

#     return {"message": "Persone deleted", "deleted_person": response.data}


# @app.put("/persons/{person_id}")
# async def update_person(
#     person_id: str, person: PersonUpdate, redis_client: redis.Redis = Depends(get_redis)
# ):
#     person_data = (
#         supabase.table("persons").select("group_id").eq("id", person_id).execute()
#     )
#     group_id = person_data.data[0]["group_id"] if person_data.data else None

#     response = (
#         supabase.table("persons")
#         .update(person.model_dump())
#         .eq("id", person_id)
#         .execute()
#     )

#     await invalidate_global_cache(redis_client, "persons")
#     if group_id:
#         await invalidate_group_cache(redis_client, group_id)

#     return {"message": "Person updated", "person": response.data}


# # Group Users
# @app.get("/members")
# async def get_members(redis_client: redis.Redis = Depends(get_redis)):
#     cache_key = "members:all"
#     cached_data = await redis_client.get(cache_key)

#     if cached_data:
#         print("Cache (All Members): Returning from Redis.")
#         return MemberListResponse.model_validate_json(cached_data)

#     response = supabase.table("group_users").select("*").execute()
#     response_data = MemberListResponse(members=response.data)

#     await redis_client.setex(cache_key, 30, response_data.model_dump_json())

#     return response_data


# @app.post("/members")
# async def add_member(
#     member: GroupUserIn, redis_client: redis.Redis = Depends(get_redis)
# ):
#     response = supabase.table("group_users").insert(member.model_dump()).execute()

#     await invalidate_global_cache(redis_client, "members")
#     await invalidate_user_cache(redis_client, member.user_id)

#     return {"message": "Member added", "member": response.data}


# @app.delete("/members/{member_id}")
# async def delete_member(member_id: str, redis_client: redis.Redis = Depends(get_redis)):
#     member_data = (
#         supabase.table("group_users").select("user_id").eq("id", member_id).execute()
#     )
#     user_id = member_data.data[0]["user_id"] if member_data.data else None

#     response = supabase.table("group_users").delete().eq("id", member_id).execute()

#     await invalidate_global_cache(redis_client, "members")
#     if user_id:
#         await invalidate_user_cache(redis_client, user_id)

#     return {"message": "Member deleted", "deleted_member": response.data}


# @app.put("/members/{member_id}")
# async def update_member(
#     member_id: str,
#     member: GroupUserUpdate,
#     redis_client: redis.Redis = Depends(get_redis),
# ):
#     member_data = (
#         supabase.table("group_users").select("user_id").eq("id", member_id).execute()
#     )
#     user_id = member_data.data[0]["user_id"] if member_data.data else None

#     response = (
#         supabase.table("group_users")
#         .update(member.model_dump())
#         .eq("id", member_id)
#         .execute()
#     )

#     await invalidate_global_cache(redis_client, "members")
#     if user_id:
#         await invalidate_user_cache(redis_client, user_id)

#     return {"message": "Member updated", "member": response.data}


# # Groups
# @app.get("/groups")
# async def get_groups(redis_client: redis.Redis = Depends(get_redis)):
#     cache_key = "groups:all"
#     cached_data = await redis_client.get(cache_key)

#     if cached_data:
#         print("Cache (All Groups): Returning from Redis.")
#         return GroupListResponse.model_validate_json(cached_data)

#     response = supabase.table("groups").select("*").execute()
#     response_data = GroupListResponse(groups=response.data)

#     await redis_client.setex(cache_key, 30, response_data.model_dump_json())

#     return response_data


# @app.get("/groups/{group_id}")
# async def get_group(group_id: str, redis_client: redis.Redis = Depends(get_redis)):
#     cache_key = f"group:{group_id}"
#     cached_data = await redis_client.get(cache_key)

#     if cached_data:
#         print("Cache (Single Group): Returning from Redis.")
#         return GroupResponse.model_validate_json(cached_data)

#     response = (
#         supabase.table("groups").select("*").eq("id", group_id).single().execute()
#     )
#     response_data = GroupResponse(group=response.data)

#     await redis_client.setex(cache_key, 30, response_data.model_dump_json())

#     return response_data


# @app.get("/groups/{group_id}/persons")
# async def get_group_persons(
#     group_id: str, redis_client: redis.Redis = Depends(get_redis)
# ):
#     cache_key = f"persons:group:{group_id}"
#     cached_data = await redis_client.get(cache_key)

#     if cached_data:
#         print("Cache (Group Persons): Returning from Redis.")
#         return GroupPersonsResponse.model_validate_json(cached_data)

#     response = supabase.table("persons").select("*").eq("group_id", group_id).execute()
#     response_data = GroupPersonsResponse(persons=response.data)

#     await redis_client.setex(cache_key, 30, response_data.model_dump_json())

#     return response_data


# @app.post("/groups")
# async def add_group(group: GroupIn, redis_client: redis.Redis = Depends(get_redis)):
#     response = supabase.table("groups").insert(group.model_dump()).execute()

#     await invalidate_global_cache(redis_client, "groups")

#     return {"message": "Group added", "group": response.data}


# @app.delete("/groups/{group_id}")
# async def delete_group(group_id: str, redis_client: redis.Redis = Depends(get_redis)):
#     response = supabase.table("groups").delete().eq("id", group_id).execute()

#     await invalidate_global_cache(redis_client, "groups")
#     await invalidate_group_cache(redis_client, group_id)

#     return {"message": "Group deleted", "deleted_group": response.data}


# @app.put("/groups/{group_id}")
# async def update_group(
#     group_id: str, group: GroupUpdate, redis_client: redis.Redis = Depends(get_redis)
# ):
#     response = (
#         supabase.table("groups").update(group.model_dump()).eq("id", group_id).execute()
#     )

#     await invalidate_global_cache(redis_client, "groups")
#     await invalidate_group_cache(redis_client, group_id)

#     return {"message": "Group updated", "group": response.data}


# @app.get("/groups/{group_id}/balances")
# async def get_group_balances(
#     group_id: str, redis_client: redis.Redis = Depends(get_redis)
# ):
#     cache_key = f"balances:group:{group_id}"
#     cached_data = await redis_client.get(cache_key)

#     if cached_data:
#         print("Cache (Group Balances): Returning from Redis.")
#         return GroupBalancesResponse.model_validate_json(cached_data)

#     # 1. Verify group exists
#     group = supabase.table("groups").select("id").eq("id", group_id).single().execute()
#     if not group.data:
#         raise HTTPException(status_code=404, detail="Group not found")

#     # 2. Get persons in group
#     persons = (
#         supabase.table("persons")
#         .select("id, name")
#         .eq("group_id", group_id)
#         .execute()
#         .data
#     )
#     if not persons:
#         response_data = GroupBalancesResponse(balances={})
#         await redis_client.setex(cache_key, 15, response_data.model_dump_json())
#         return response_data

#     balances = {
#         person["id"]: {
#             "name": person["name"],
#             "paid": 0.0,
#             "owes": 0.0,
#             "balance": 0.0,
#         }
#         for person in persons
#     }

#     # 3. Get all expenses for this group
#     expenses = (
#         supabase.table("expenses")
#         .select("id, amount, payer_id")
#         .eq("group_id", group_id)
#         .execute()
#         .data
#     )
#     expense_ids = [e["id"] for e in expenses]

#     # 4. Aggregate "paid" by payer
#     for e in expenses:
#         payer_id = e["payer_id"]
#         if payer_id in balances:
#             balances[payer_id]["paid"] += float(e["amount"])

#     # 5. Get debtors only for this group's expenses
#     if expense_ids:
#         debtors = (
#             supabase.table("expenses_debtors")
#             .select("person_id, amount, expense_id")
#             .in_("expense_id", expense_ids)
#             .execute()
#             .data
#         )

#         for d in debtors:
#             if d["person_id"] in balances:
#                 balances[d["person_id"]]["owes"] += float(d["amount"])

#     # 6. Compute net balance
#     for person_id, data in balances.items():
#         data["balance"] = data["paid"] - data["owes"]

#     response_data = GroupBalancesResponse(balances=balances)
#     await redis_client.setex(cache_key, 15, response_data.model_dump_json())

#     return response_data


# # Users
# @app.get("/users/{user_id}/groups")
# async def get_user_groups(user_id: str, redis_client: redis.Redis = Depends(get_redis)):
#     cache_key = f"user:groups:{user_id}"
#     cached_data = await redis_client.get(cache_key)

#     if cached_data:
#         print("Cache (User Groups): Returning from Redis.")
#         return UserGroupsResponse.model_validate_json(cached_data)

#     response = (
#         supabase.table("group_users")
#         .select("group:groups(id, name, created_at)")
#         .eq("user_id", user_id)
#         .execute()
#     )

#     groups_data = [g["group"] for g in response.data]
#     response_data = UserGroupsResponse(groups=groups_data)

#     await redis_client.setex(cache_key, 60, response_data.model_dump_json())

#     return response_data
