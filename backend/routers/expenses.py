from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
import time

# Models
from models.expense import ExpenseListResponse, ExpenseCreate, ExpenseUpdate

# Helpers
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

# Middlewares
from middlewares.rate_limiter import (
    basic_rate_limit,
    strict_rate_limit,
    expensive_rate_limit,
)
from middlewares.logger import get_logger, log_cache_operation, log_database_operation
from middlewares.monitoring import track_cache_operation, track_database_operation

# Constants
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

logger = get_logger()


# Expenses
@router.get("/", response_model=ExpenseListResponse)
@basic_rate_limit()
async def get_expenses(
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = EXPENSES_ALL
    start_time = time.time()

    logger.info("Fetching all expenses")

    try:
        # Try to get from cache
        expenses = await get_cached_items(redis_client, cache_key)

        if expenses:
            log_cache_operation("get", cache_key, True)
            track_cache_operation("get", True)
            logger.info(f"Expenses retrieved from cache | Count: {len(expenses)}")
        else:
            log_cache_operation("get", cache_key, False)
            track_cache_operation("get", False)

            # Get from database
            db_start = time.time()
            expenses = await get_all_expenses_from_db(supabase)
            db_duration = time.time() - db_start

            log_database_operation("select", "expenses", db_duration)
            track_database_operation("select", "expenses", db_duration)

            # Cache the results
            cache_items(background_tasks, redis_client, cache_key, expenses)
            log_cache_operation("set", cache_key)

            logger.info(
                f"Expenses retrieved from database | Count: {len(expenses)} | DB Duration: {db_duration:.3f}s"
            )

        total_duration = time.time() - start_time
        logger.info(f"Get expenses completed | Total Duration: {total_duration:.3f}s")

        return ExpenseListResponse(expenses=expenses)

    except Exception as e:
        logger.error(f"Error fetching expenses: {str(e)}")
        raise HTTPException(
            status_code=500, detail=ErrorMessages.ERROR_RETRIEVING_EXPENSES
        )


@router.post("/")
@strict_rate_limit()
async def add_expense(
    expense: ExpenseCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(
        f"Adding new expense | Amount: {expense.amount} | Group: {expense.group_id}"
    )

    # Validate expense amount
    if expense.amount <= 0:
        logger.warning(f"Invalid expense amount: {expense.amount}")
        raise HTTPException(
            status_code=400, detail=ErrorMessages.INVALID_EXPENSE_AMOUNT
        )

    # Validate debtors exist
    if not expense.debtors or len(expense.debtors) == 0:
        logger.warning("No debtors provided for expense")
        raise HTTPException(status_code=400, detail="At least one debtor is required")

    try:
        # Create expense with timing
        db_start = time.time()
        expense_data = await create_expense_record(supabase, expense)
        db_duration = time.time() - db_start

        log_database_operation("insert", "expenses", db_duration)
        track_database_operation("insert", "expenses", db_duration)

        if not expense_data:
            logger.error("Failed to create expense record")
            raise HTTPException(
                status_code=500, detail=ErrorMessages.ERROR_ADDING_EXPENSE
            )

        # Create debtors with timing
        db_start = time.time()
        debtors_data = await create_debtors_records(
            supabase, expense_data["id"], expense.amount, expense.debtors
        )
        db_duration = time.time() - db_start

        log_database_operation("insert", "expense_debtors", db_duration)
        track_database_operation("insert", "expense_debtors", db_duration)

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

        log_cache_operation("update", global_cache_key)
        log_cache_operation("update", group_cache_key)

        total_duration = time.time() - start_time
        logger.info(
            f"Expense added successfully | ID: {expense_data['id']} | Total Duration: {total_duration:.3f}s"
        )

        return {
            "message": SuccessMessages.EXPENSE_ADDED,
            "expense": expense_data,
            "debtors": debtors_data,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding expense: {str(e)}")
        raise HTTPException(status_code=500, detail=ErrorMessages.ERROR_ADDING_EXPENSE)


@router.delete("/{expense_id}")
@expensive_rate_limit()
async def delete_expense(
    expense_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(f"Deleting expense | ID: {expense_id}")

    try:
        # Get group_id before deletion
        db_start = time.time()
        group_id = await get_expense_group_id(supabase, expense_id)
        db_duration = time.time() - db_start

        log_database_operation("select", "expenses", db_duration)
        track_database_operation("select", "expenses", db_duration)

        if group_id is None:
            logger.warning(f"Expense not found | ID: {expense_id}")
            raise HTTPException(status_code=404, detail=ErrorMessages.EXPENSE_NOT_FOUND)

        # Delete expense
        db_start = time.time()
        response = await delete_expense_from_db(supabase, expense_id)
        db_duration = time.time() - db_start

        log_database_operation("delete", "expenses", db_duration)
        track_database_operation("delete", "expenses", db_duration)

        if not response.data:
            logger.warning(f"Expense deletion failed | ID: {expense_id}")
            raise HTTPException(status_code=404, detail=ErrorMessages.EXPENSE_NOT_FOUND)

        # Remove from cache in multiple locations
        global_cache_key = EXPENSES_ALL

        remove_item_from_cache(
            background_tasks, redis_client, global_cache_key, expense_id
        )
        log_cache_operation("delete", global_cache_key)

        if group_id:
            group_cache_key = group_expenses_cache_key(group_id)
            remove_item_from_cache(
                background_tasks, redis_client, group_cache_key, expense_id
            )
            balances_cache_key = group_balances_cache_key(group_id)
            invalidate_cache(background_tasks, redis_client, balances_cache_key)
            log_cache_operation("delete", group_cache_key)
            log_cache_operation("invalidate", balances_cache_key)

        total_duration = time.time() - start_time
        logger.info(
            f"Expense deleted successfully | ID: {expense_id} | Total Duration: {total_duration:.3f}s"
        )

        return {
            "message": SuccessMessages.EXPENSE_DELETED,
            "deleted_expense": response.data,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting expense | ID: {expense_id} | Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=ErrorMessages.ERROR_DELETING_EXPENSE
        )


@router.put("/{expense_id}")
@strict_rate_limit()
async def update_expense(
    expense_id: str,
    expense: ExpenseUpdate,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(f"Updating expense | ID: {expense_id}")

    try:
        # Get group_id for cache update
        db_start = time.time()
        group_id = await get_expense_group_id(supabase, expense_id)
        db_duration = time.time() - db_start

        log_database_operation("select", "expenses", db_duration)
        track_database_operation("select", "expenses", db_duration)

        if group_id is None:
            logger.warning(f"Expense not found for update | ID: {expense_id}")
            raise HTTPException(status_code=404, detail=ErrorMessages.EXPENSE_NOT_FOUND)

        # Update expense
        db_start = time.time()
        response = await update_expense_in_db(supabase, expense_id, expense)
        db_duration = time.time() - db_start

        log_database_operation("update", "expenses", db_duration)
        track_database_operation("update", "expenses", db_duration)

        if not response.data:
            logger.warning(f"Expense update failed | ID: {expense_id}")
            raise HTTPException(status_code=404, detail=ErrorMessages.EXPENSE_NOT_FOUND)

        # Update cache in multiple locations
        expense_data = response.data[0]
        global_cache_key = EXPENSES_ALL

        update_item_cache(
            background_tasks, redis_client, global_cache_key, expense_data
        )
        log_cache_operation("update", global_cache_key)

        if group_id:
            group_cache_key = group_expenses_cache_key(group_id)
            update_item_cache(
                background_tasks, redis_client, group_cache_key, expense_data
            )
            log_cache_operation("update", group_cache_key)

        total_duration = time.time() - start_time
        logger.info(
            f"Expense updated successfully | ID: {expense_id} | Total Duration: {total_duration:.3f}s"
        )

        return {"message": SuccessMessages.EXPENSE_UPDATED, "expense": response.data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating expense | ID: {expense_id} | Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=ErrorMessages.ERROR_UPDATING_EXPENSE
        )
