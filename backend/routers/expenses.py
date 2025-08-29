from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends
import redis.asyncio as redis
import json
from models.expense import ExpenseListResponse
import asyncio

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
)


async def set_cache(redis_client, key, field, value):
    await redis_client.hset(key, field, value)


# Expenses
@router.get("/", response_model=ExpenseListResponse)
async def get_expenses(
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = "expenses:all"
    data = await redis_client.hgetall(cache_key)

    if data:
        expenses = [json.loads(v) for v in data.values()]
    else:
        expenses = supabase.table("expenses").select("*").execute().data
        for e in expenses:
            background_tasks.add_task(
                set_cache, redis_client, cache_key, e["id"], json.dumps(e)
            )

    return ExpenseListResponse(expenses=expenses)


# @router.get("/groups/{group_id}/expenses")
# async def get_expenses_for_group(group_id: str):
#     cache_key = f"groups:{group_id}:expenses"
#     data = await get_cache(cache_key)

#     if not data:

#         data = (
#             supabase.table("expenses")
#             .select("*")
#             .eq("group_id", group_id)
#             .execute()
#             .data
#         )
#         background_tasks.add_task(set_cache, data, cache_key)

#     return ExpenseListResponse(expenses=expenses_list)


# @router.post("/")
# async def add_expense(
#     expense: ExpenseCreate, redis_client: redis.Redis = Depends(get_redis)
# ):

#     new_expense = {
#         "name": expense.name,
#         "amount": expense.amount,
#         "payer_id": expense.payer_id,
#         "group_id": expense.group_id,
#     }
#     expense_response = supabase.table("expenses").insert(new_expense).execute()

#     # Get inserted expense id
#     expense_id = expense_response.data[0]["id"]

#     # Share expense amount equally between debtors
#     share_amount = expense.amount / len(expense.debtors)

#     debtors_data = [
#         {"expense_id": expense_id, "person_id": debtor_id, "amount": share_amount}
#         for debtor_id in expense.debtors
#     ]

#     response = supabase.table("expenses_debtors").insert(debtors_data).execute()

#     await invalidate_global_cache(redis_client, "expenses")
#     await invalidate_global_cache(redis_client, "debtors")
#     await invalidate_group_cache(redis_client, expense.group_id)

#     return {
#         "message": "Expense added",
#         "expense": expense_response.data[0],
#         "debtors": response.data,
#     }


# @router.delete("/{expense_id}")
# async def delete_expense(
#     expense_id: str, redis_client: redis.Redis = Depends(get_redis)
# ):
#     expense_data = (
#         supabase.table("expenses").select("group_id").eq("id", expense_id).execute()
#     )
#     group_id = expense_data.data[0]["group_id"] if expense_data.data else None

#     response = supabase.table("expenses").delete().eq("id", expense_id).execute()

#     await invalidate_global_cache(redis_client, "expenses")
#     await invalidate_global_cache(redis_client, "debtors")
#     if group_id:
#         await invalidate_group_cache(redis_client, group_id)

#     return {"message": "Expense deleted", "deleted_expense": response.data}


# @router.put("/{expense_id}")
# async def update_expense(
#     expense_id: str,
#     expense: ExpenseUpdate,
#     redis_client: redis.Redis = Depends(get_redis),
# ):
#     expense_data = (
#         supabase.table("expenses").select("group_id").eq("id", expense_id).execute()
#     )
#     group_id = expense_data.data[0]["group_id"] if expense_data.data else None

#     response = (
#         supabase.table("expenses")
#         .update(expense.model_dump())
#         .eq("id", expense_id)
#         .execute()
#     )

#     await invalidate_global_cache(redis_client, "expenses")
#     if group_id:
#         await invalidate_group_cache(redis_client, group_id)

#     return {"message": "Expense updated", "expense": response.data}
