from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends
import redis.asyncio as redis
import json
from models.expense import ExpenseListResponse, ExpenseCreate, ExpenseUpdate
import asyncio

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
)


# Expenses
@router.get("/", response_model=ExpenseListResponse)
async def get_expenses(
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = "expenses:all"

    # Try to get from cache
    expenses = await get_cached_expenses(redis_client, cache_key)

    # If not in cache, get from database and cache it
    if not expenses:
        expenses = get_all_expenses_from_db(supabase)
        await cache_expenses(background_tasks, redis_client, cache_key, expenses)

    return ExpenseListResponse(expenses=expenses)


@router.post("/")
async def add_expense(
    expense: ExpenseCreate,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    # Create expense
    expense_data = await create_expense_record(supabase, expense)

    # Create debtors
    debtors_data = await create_debtors_records(
        supabase, expense_data["id"], expense.amount, expense.debtors
    )

    # Update cache
    await update_expense_cache(
        background_tasks, redis_client, expense_data, expense.group_id
    )

    return {
        "message": "Expense added",
        "expense": expense_data,
        "debtors": debtors_data,
    }


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: str,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    # Get group_id before deletion
    group_id = await get_expense_group_id(supabase, expense_id)

    # Delete expense
    response = await delete_expense_from_db(supabase, expense_id)

    # Remove from cache
    await remove_expense_from_cache(
        background_tasks, redis_client, expense_id, group_id
    )

    return {"message": "Expense deleted", "deleted_expense": response.data}


@router.put("/{expense_id}")
async def update_expense(
    expense_id: str,
    expense: ExpenseUpdate,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    # Get group_id for cache update
    group_id = await get_expense_group_id(supabase, expense_id)

    # Update expense
    response = await update_expense_in_db(supabase, expense_id, expense)

    # Update cache
    await update_expense_cache(
        background_tasks, redis_client, response.data[0], group_id
    )

    return {"message": "Expense updated", "expense": response.data}
