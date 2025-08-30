from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from models.expense import ExpenseListResponse, ExpenseCreate, ExpenseUpdate
from helpers.cache_helpers import (
    get_cached_items,
    cache_items,
    invalidate_cache,
    update_item_cache,
    remove_item_from_cache,
)
from helpers.expense_helpers import (
    get_all_expenses_from_db,
    create_expense_record,
    create_debtors_records,
    get_expense_group_id,
    delete_expense_from_db,
    update_expense_in_db,
)
from constants.cache_keys import (
    EXPENSES_ALL,
    group_expenses_cache_key,
    group_balances_cache_key,
)
from constants.api_messages import SuccessMessages, ErrorMessages

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
    cache_key = EXPENSES_ALL

    # Try to get from cache
    expenses = await get_cached_items(redis_client, cache_key)

    # If not in cache, get from database and cache it
    if not expenses:
        expenses = await get_all_expenses_from_db(supabase)
        cache_items(background_tasks, redis_client, cache_key, expenses)

    return ExpenseListResponse(expenses=expenses)


@router.post("/")
async def add_expense(
    expense: ExpenseCreate,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    # Validate expense amount
    if expense.amount <= 0:
        raise HTTPException(
            status_code=400, detail=ErrorMessages.INVALID_EXPENSE_AMOUNT
        )

    # Validate debtors exist
    if not expense.debtors or len(expense.debtors) == 0:
        raise HTTPException(status_code=400, detail="At least one debtor is required")

    try:
        # Create expense
        expense_data = await create_expense_record(supabase, expense)
        if not expense_data:
            raise HTTPException(
                status_code=500, detail=ErrorMessages.ERROR_ADDING_EXPENSE
            )

        # Create debtors
        debtors_data = await create_debtors_records(
            supabase, expense_data["id"], expense.amount, expense.debtors
        )

        # Update cache in multiple locations
        global_cache_key = EXPENSES_ALL
        group_cache_key = group_expenses_cache_key(expense.group_id)

        update_item_cache(
            background_tasks, redis_client, global_cache_key, expense_data
        )
        update_item_cache(
            background_tasks,
            redis_client,
            group_cache_key,
            expense_data,
        )

        return {
            "message": SuccessMessages.EXPENSE_ADDED,
            "expense": expense_data,
            "debtors": debtors_data,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorMessages.ERROR_ADDING_EXPENSE)


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: str,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    try:
        # Get group_id before deletion
        group_id = await get_expense_group_id(supabase, expense_id)
        if group_id is None:
            raise HTTPException(status_code=404, detail=ErrorMessages.EXPENSE_NOT_FOUND)

        # Delete expense
        response = await delete_expense_from_db(supabase, expense_id)
        if not response.data:
            raise HTTPException(status_code=404, detail=ErrorMessages.EXPENSE_NOT_FOUND)

        # Remove from cache in multiple locations
        global_cache_key = EXPENSES_ALL

        remove_item_from_cache(
            background_tasks, redis_client, global_cache_key, expense_id
        )
        if group_id:
            group_cache_key = group_expenses_cache_key(group_id)
            remove_item_from_cache(
                background_tasks, redis_client, group_cache_key, expense_id
            )
            balances_cache_key = group_balances_cache_key(group_id)
            invalidate_cache(background_tasks, redis_client, balances_cache_key)

        return {
            "message": SuccessMessages.EXPENSE_DELETED,
            "deleted_expense": response.data,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=ErrorMessages.ERROR_DELETING_EXPENSE
        )


@router.put("/{expense_id}")
async def update_expense(
    expense_id: str,
    expense: ExpenseUpdate,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    try:
        # Validate expense amount if provided
        if (
            hasattr(expense, "amount")
            and expense.amount is not None
            and expense.amount <= 0
        ):
            raise HTTPException(
                status_code=400, detail=ErrorMessages.INVALID_EXPENSE_AMOUNT
            )

        # Get group_id for cache update
        group_id = await get_expense_group_id(supabase, expense_id)
        if group_id is None:
            raise HTTPException(status_code=404, detail=ErrorMessages.EXPENSE_NOT_FOUND)

        # Update expense
        response = await update_expense_in_db(supabase, expense_id, expense)
        if not response.data:
            raise HTTPException(status_code=404, detail=ErrorMessages.EXPENSE_NOT_FOUND)

        # Update cache in multiple locations
        expense_data = response.data[0]
        global_cache_key = EXPENSES_ALL

        update_item_cache(
            background_tasks, redis_client, global_cache_key, expense_data
        )
        if group_id:
            group_cache_key = group_expenses_cache_key(group_id)
            update_item_cache(
                background_tasks, redis_client, group_cache_key, expense_data
            )

        return {"message": SuccessMessages.EXPENSE_UPDATED, "expense": response.data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=ErrorMessages.ERROR_UPDATING_EXPENSE
        )
