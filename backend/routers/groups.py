from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends
import redis.asyncio as redis
import json
from models.expense import ExpenseListResponse
import asyncio

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)


# # Groups
# @router.get("/groups")
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


# @router.get("/groups/{group_id}")
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


@router.get("/{group_id}/expenses", response_model=ExpenseListResponse)
async def get_expenses_for_group(
    group_id: str,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = f"groups:{group_id}:expenses"
    data = await redis_client.hgetall(cache_key)

    if data:
        expenses = [json.loads(v) for v in data.values()]
    else:
        expenses = (
            supabase.table("expenses")
            .select("*")
            .eq("group_id", group_id)
            .execute()
            .data
        )
        for e in expenses:
            background_tasks.add_task(
                redis_client.hset, cache_key, e["id"], json.dumps(e)
            )

    return ExpenseListResponse(expenses=expenses)


# @router.get("/groups/{group_id}/persons")
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


# @router.post("/groups")
# async def add_group(group: GroupIn, redis_client: redis.Redis = Depends(get_redis)):
#     response = supabase.table("groups").insert(group.model_dump()).execute()

#     await invalidate_global_cache(redis_client, "groups")

#     return {"message": "Group added", "group": response.data}


# @router.delete("/groups/{group_id}")
# async def delete_group(group_id: str, redis_client: redis.Redis = Depends(get_redis)):
#     response = supabase.table("groups").delete().eq("id", group_id).execute()

#     await invalidate_global_cache(redis_client, "groups")
#     await invalidate_group_cache(redis_client, group_id)

#     return {"message": "Group deleted", "deleted_group": response.data}


# @router.put("/groups/{group_id}")
# async def update_group(
#     group_id: str, group: GroupUpdate, redis_client: redis.Redis = Depends(get_redis)
# ):
#     response = (
#         supabase.table("groups").update(group.model_dump()).eq("id", group_id).execute()
#     )

#     await invalidate_global_cache(redis_client, "groups")
#     await invalidate_group_cache(redis_client, group_id)

#     return {"message": "Group updated", "group": response.data}


# @router.get("/groups/{group_id}/balances")
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
