from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
import time

# Models
from models.debtor import ExpenseDebtorIn, ExpenseDebtorUpdate, DebtorListResponse

# Helpers
from helpers.cache_helpers import get_cached_items, cache_items, invalidate_cache
from helpers.debtor_helpers import (
    get_all_debtors_from_db,
    get_group_debtors_from_db,
    create_debtor_record,
    get_debtor_expense_id,
    get_expense_group_id_from_expense,
    delete_debtor_from_db,
    update_debtor_in_db,
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
from constants.cache_keys import DEBTORS_ALL, group_debtors_cache_key
from constants.api_messages import SuccessMessages, ErrorMessages

router = APIRouter(
    prefix="/debtors",
    tags=["debtors"],
)

logger = get_logger()


@router.get("/", response_model=DebtorListResponse)
@basic_rate_limit()
async def get_debtors(
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = DEBTORS_ALL
    start_time = time.time()

    logger.info("Fetching all debtors")

    try:
        # Try to get from cache
        debtors = await get_cached_items(redis_client, cache_key)

        if debtors:
            log_cache_operation("get", cache_key, True)
            track_cache_operation("get", True)
            logger.info(f"Debtors retrieved from cache | Count: {len(debtors)}")
        else:
            log_cache_operation("get", cache_key, False)
            track_cache_operation("get", False)

            # Get from database
            db_start = time.time()
            debtors = await get_all_debtors_from_db(supabase)
            db_duration = time.time() - db_start

            log_database_operation("select", "debtors", db_duration)
            track_database_operation("select", "debtors", db_duration)

            # Cache the results
            cache_items(background_tasks, redis_client, cache_key, debtors)
            log_cache_operation("set", cache_key)

            logger.info(
                f"Debtors retrieved from database | Count: {len(debtors)} | DB Duration: {db_duration:.3f}s"
            )

        total_duration = time.time() - start_time
        logger.info(f"Get debtors completed | Total Duration: {total_duration:.3f}s")

        return DebtorListResponse(debtors=debtors)

    except Exception as e:
        logger.error(f"Error fetching debtors: {str(e)}")
        raise HTTPException(
            status_code=500, detail=ErrorMessages.ERROR_RETRIEVING_DEBTORS
        )


@router.get("/{group_id}", response_model=DebtorListResponse)
@basic_rate_limit()
async def get_debtors_for_group(
    group_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = group_debtors_cache_key(group_id)
    start_time = time.time()

    logger.info(f"Fetching debtors for group | ID: {group_id}")

    try:
        # Try to get from cache
        debtors = await get_cached_items(redis_client, cache_key)

        if debtors:
            log_cache_operation("get", cache_key, True)
            track_cache_operation("get", True)
            logger.info(
                f"Group debtors retrieved from cache | Group: {group_id} | Count: {len(debtors)}"
            )
        else:
            log_cache_operation("get", cache_key, False)
            track_cache_operation("get", False)

            # Get from database
            db_start = time.time()
            debtors = await get_group_debtors_from_db(supabase, group_id)
            db_duration = time.time() - db_start

            log_database_operation("select", "debtors", db_duration)
            track_database_operation("select", "debtors", db_duration)

            # Cache the results
            cache_items(background_tasks, redis_client, cache_key, debtors)
            log_cache_operation("set", cache_key)

            logger.info(
                f"Group debtors retrieved from database | Group: {group_id} | Count: {len(debtors)} | DB Duration: {db_duration:.3f}s"
            )

        total_duration = time.time() - start_time
        logger.info(
            f"Get group debtors completed | Group: {group_id} | Total Duration: {total_duration:.3f}s"
        )

        return DebtorListResponse(debtors=debtors)

    except Exception as e:
        logger.error(
            f"Error fetching group debtors | Group: {group_id} | Error: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail=ErrorMessages.ERROR_RETRIEVING_GROUP_DEBTORS
        )


@router.post("/")
@strict_rate_limit()
async def add_debtor(
    debtor: ExpenseDebtorIn,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(f"Adding new debtor | Expense: {debtor.expense_id}")

    try:
        # Get group_id for cache invalidation
        db_start = time.time()
        group_id = await get_expense_group_id_from_expense(supabase, debtor.expense_id)
        db_duration = time.time() - db_start

        log_database_operation("select", "expenses", db_duration)
        track_database_operation("select", "expenses", db_duration)

        db_start = time.time()
        debtor_data = await create_debtor_record(supabase, debtor)
        db_duration = time.time() - db_start

        log_database_operation("insert", "debtors", db_duration)
        track_database_operation("insert", "debtors", db_duration)

        if not debtor_data:
            logger.error("Failed to create debtor record")
            raise HTTPException(500, ErrorMessages.ERROR_ADDING_DEBTOR)

        # Invalidate caches
        global_cache_key = DEBTORS_ALL
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        log_cache_operation("invalidate", global_cache_key)

        if group_id:
            group_cache_key = group_debtors_cache_key(group_id)
            invalidate_cache(background_tasks, redis_client, group_cache_key)
            log_cache_operation("invalidate", group_cache_key)

        total_duration = time.time() - start_time
        logger.info(
            f"Debtor added successfully | ID: {debtor_data['id']} | Expense: {debtor.expense_id} | Total Duration: {total_duration:.3f}s"
        )

        return {"message": SuccessMessages.DEBTOR_ADDED, "debtor": debtor_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error adding debtor | Expense: {debtor.expense_id} | Error: {str(e)}"
        )
        raise HTTPException(500, ErrorMessages.ERROR_ADDING_DEBTOR)


@router.delete("/{debtor_id}")
@expensive_rate_limit()
async def delete_debtor(
    debtor_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(f"Deleting debtor | ID: {debtor_id}")

    try:
        # Get expense_id and group_id for cache invalidation
        db_start = time.time()
        expense_id = await get_debtor_expense_id(supabase, debtor_id)
        db_duration = time.time() - db_start

        log_database_operation("select", "debtors", db_duration)
        track_database_operation("select", "debtors", db_duration)

        if expense_id is None:
            logger.warning(f"Debtor not found | ID: {debtor_id}")
            raise HTTPException(404, ErrorMessages.DEBTOR_NOT_FOUND)

        db_start = time.time()
        group_id = await get_expense_group_id_from_expense(supabase, expense_id)
        db_duration = time.time() - db_start

        log_database_operation("select", "expenses", db_duration)
        track_database_operation("select", "expenses", db_duration)

        # Delete debtor
        db_start = time.time()
        response = await delete_debtor_from_db(supabase, debtor_id)
        db_duration = time.time() - db_start

        log_database_operation("delete", "debtors", db_duration)
        track_database_operation("delete", "debtors", db_duration)

        if not response:
            logger.warning(f"Debtor deletion failed | ID: {debtor_id}")
            raise HTTPException(404, ErrorMessages.DEBTOR_NOT_FOUND)

        # Invalidate caches
        global_cache_key = DEBTORS_ALL
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        log_cache_operation("invalidate", global_cache_key)

        if group_id:
            group_cache_key = group_debtors_cache_key(group_id)
            invalidate_cache(background_tasks, redis_client, group_cache_key)
            log_cache_operation("invalidate", group_cache_key)

        total_duration = time.time() - start_time
        logger.info(
            f"Debtor deleted successfully | ID: {debtor_id} | Total Duration: {total_duration:.3f}s"
        )

        return {"message": SuccessMessages.DEBTOR_DELETED, "deleted_debtor": response}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting debtor | ID: {debtor_id} | Error: {str(e)}")
        raise HTTPException(500, ErrorMessages.ERROR_DELETING_DEBTOR)


@router.put("/{debtor_id}")
@strict_rate_limit()
async def update_debtor(
    debtor_id: str,
    debtor: ExpenseDebtorUpdate,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(f"Updating debtor | ID: {debtor_id}")

    try:
        # Get expense_id and group_id for cache invalidation
        db_start = time.time()
        expense_id = await get_debtor_expense_id(supabase, debtor_id)
        db_duration = time.time() - db_start

        log_database_operation("select", "debtors", db_duration)
        track_database_operation("select", "debtors", db_duration)

        if expense_id is None:
            logger.warning(f"Debtor not found for update | ID: {debtor_id}")
            raise HTTPException(404, ErrorMessages.DEBTOR_NOT_FOUND)

        db_start = time.time()
        group_id = await get_expense_group_id_from_expense(supabase, expense_id)
        db_duration = time.time() - db_start

        log_database_operation("select", "expenses", db_duration)
        track_database_operation("select", "expenses", db_duration)

        # Update debtor
        db_start = time.time()
        response = await update_debtor_in_db(supabase, debtor_id, debtor)
        db_duration = time.time() - db_start

        log_database_operation("update", "debtors", db_duration)
        track_database_operation("update", "debtors", db_duration)

        if not response:
            logger.warning(f"Debtor update failed | ID: {debtor_id}")
            raise HTTPException(404, ErrorMessages.DEBTOR_NOT_FOUND)

        # Invalidate caches
        global_cache_key = DEBTORS_ALL
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        log_cache_operation("invalidate", global_cache_key)

        if group_id:
            group_cache_key = group_debtors_cache_key(group_id)
            invalidate_cache(background_tasks, redis_client, group_cache_key)
            log_cache_operation("invalidate", group_cache_key)

        total_duration = time.time() - start_time
        logger.info(
            f"Debtor updated successfully | ID: {debtor_id} | Total Duration: {total_duration:.3f}s"
        )

        return {"message": SuccessMessages.DEBTOR_UPDATED, "debtor": response}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating debtor | ID: {debtor_id} | Error: {str(e)}")
        raise HTTPException(500, ErrorMessages.ERROR_UPDATING_DEBTOR)
