import time
from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

# Models
from models.expense import ExpenseListResponse
from models.group import (
    GroupIn,
    GroupUpdate,
    GroupListResponse,
    GroupResponse,
    GroupPersonsResponse,
    GroupBalancesResponse,
)

# Helpers
from helpers.cache_helpers import (
    cache_single_object,
    get_cached_items,
    cache_items,
    get_cached_single_object,
    invalidate_cache,
    invalidate_multiple_caches,
)

from helpers.group_helpers import (
    get_all_groups_from_db,
    get_group_by_id_from_db,
    get_group_persons_from_db,
    create_group_record,
    delete_group_from_db,
    update_group_in_db,
    calculate_group_balances,
)

from helpers.expense_helpers import get_group_expenses_from_db

# Middlewares
from middlewares.logger import log_cache_operation, log_database_operation, get_logger
from middlewares.monitoring import track_cache_operation, track_database_operation
from middlewares.rate_limiter import (
    basic_rate_limit,
    strict_rate_limit,
    expensive_rate_limit,
)

# Constants
from constants.api_messages import SuccessMessages, ErrorMessages
from constants.cache_keys import (
    GROUPS_ALL,
    group_cache_key,
    group_expenses_cache_key,
    group_persons_cache_key,
    group_balances_cache_key,
)

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)

logger = get_logger()


# Groups
@router.get("/", response_model=GroupListResponse)
@basic_rate_limit()
async def get_groups(
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = GROUPS_ALL
    start_time = time.time()

    logger.info("Fetching all groups")

    try:
        # Try to get from cache
        groups = await get_cached_items(redis_client, cache_key)

        if groups:
            log_cache_operation("get", cache_key, True)
            track_cache_operation("get", True)
            logger.info(f"Groups retrieved from cache | Count: {len(groups)}")
        else:
            log_cache_operation("get", cache_key, False)
            track_cache_operation("get", False)

            # Get from database
            db_start = time.time()
            groups = await get_all_groups_from_db(supabase)
            db_duration = time.time() - db_start

            log_database_operation("select", "groups", db_duration)
            track_database_operation("select", "groups", db_duration)

            # Cache the results
            cache_items(background_tasks, redis_client, cache_key, groups)
            log_cache_operation("set", cache_key)

            logger.info(
                f"Groups retrieved from database | Count: {len(groups)} | DB Duration: {db_duration:.3f}s"
            )

        total_duration = time.time() - start_time
        logger.info(f"Get groups completed | Total Duration: {total_duration:.3f}s")

        return GroupListResponse(groups=groups)

    except Exception as e:
        logger.error(f"Error fetching groups: {str(e)}")
        raise HTTPException(
            status_code=500, detail=ErrorMessages.ERROR_RETRIEVING_GROUPS
        )


@router.get("/{group_id}", response_model=GroupResponse)
@basic_rate_limit()
async def get_group(
    group_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = group_cache_key(group_id)
    start_time = time.time()

    logger.info(f"Fetching group | ID: {group_id}")

    try:
        # Try to get from cache
        group = await get_cached_single_object(redis_client, cache_key)

        if group:
            log_cache_operation("get", cache_key, True)
            track_cache_operation("get", True)
            logger.info(f"Group retrieved from cache | ID: {group_id}")
        else:
            log_cache_operation("get", cache_key, False)
            track_cache_operation("get", False)

            # Get from database
            db_start = time.time()
            group = await get_group_by_id_from_db(supabase, group_id)
            db_duration = time.time() - db_start

            log_database_operation("select", "groups", db_duration)
            track_database_operation("select", "groups", db_duration)

            # Cache the result
            cache_single_object(background_tasks, redis_client, cache_key, group)
            log_cache_operation("set", cache_key)

            logger.info(
                f"Group retrieved from database | ID: {group_id} | DB Duration: {db_duration:.3f}s"
            )

        total_duration = time.time() - start_time
        logger.info(
            f"Get group completed | ID: {group_id} | Total Duration: {total_duration:.3f}s"
        )

        return GroupResponse(group=group)

    except Exception as e:
        logger.error(f"Error fetching group | ID: {group_id} | Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=ErrorMessages.ERROR_RETRIEVING_GROUP
        )


@router.get("/{group_id}/expenses", response_model=ExpenseListResponse)
@basic_rate_limit()
async def get_expenses_for_group(
    group_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = group_expenses_cache_key(group_id)
    start_time = time.time()

    logger.info(f"Fetching expenses for group | ID: {group_id}")

    try:
        # Try to get from cache
        expenses = await get_cached_items(redis_client, cache_key)

        if expenses:
            log_cache_operation("get", cache_key, True)
            track_cache_operation("get", True)
            logger.info(
                f"Group expenses retrieved from cache | Group: {group_id} | Count: {len(expenses)}"
            )
        else:
            log_cache_operation("get", cache_key, False)
            track_cache_operation("get", False)

            # Get from database
            db_start = time.time()
            expenses = await get_group_expenses_from_db(supabase, group_id)
            db_duration = time.time() - db_start

            log_database_operation("select", "expenses", db_duration)
            track_database_operation("select", "expenses", db_duration)

            # Cache the results
            cache_items(background_tasks, redis_client, cache_key, expenses)
            log_cache_operation("set", cache_key)

            logger.info(
                f"Group expenses retrieved from database | Group: {group_id} | Count: {len(expenses)} | DB Duration: {db_duration:.3f}s"
            )

        total_duration = time.time() - start_time
        logger.info(
            f"Get group expenses completed | Group: {group_id} | Total Duration: {total_duration:.3f}s"
        )

        return ExpenseListResponse(expenses=expenses)

    except Exception as e:
        logger.error(
            f"Error fetching group expenses | Group: {group_id} | Error: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail=ErrorMessages.ERROR_RETRIEVING_GROUP_EXPENSES
        )


@router.get("/{group_id}/persons", response_model=GroupPersonsResponse)
@basic_rate_limit()
async def get_group_persons(
    group_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = group_persons_cache_key(group_id)
    start_time = time.time()

    logger.info(f"Fetching persons for group | ID: {group_id}")

    try:
        # Try to get from cache
        persons = await get_cached_items(redis_client, cache_key)

        if persons:
            log_cache_operation("get", cache_key, True)
            track_cache_operation("get", True)
            logger.info(
                f"Group persons retrieved from cache | Group: {group_id} | Count: {len(persons)}"
            )
        else:
            log_cache_operation("get", cache_key, False)
            track_cache_operation("get", False)

            # Get from database
            db_start = time.time()
            persons = await get_group_persons_from_db(supabase, group_id)
            db_duration = time.time() - db_start

            log_database_operation("select", "persons", db_duration)
            track_database_operation("select", "persons", db_duration)

            # Cache the results
            cache_items(background_tasks, redis_client, cache_key, persons)
            log_cache_operation("set", cache_key)

            logger.info(
                f"Group persons retrieved from database | Group: {group_id} | Count: {len(persons)} | DB Duration: {db_duration:.3f}s"
            )

        total_duration = time.time() - start_time
        logger.info(
            f"Get group persons completed | Group: {group_id} | Total Duration: {total_duration:.3f}s"
        )

        return GroupPersonsResponse(persons=persons)

    except Exception as e:
        logger.error(
            f"Error fetching group persons | Group: {group_id} | Error: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail=ErrorMessages.ERROR_RETRIEVING_GROUP_PERSONS
        )


@router.post("/")
@strict_rate_limit()
async def add_group(
    group: GroupIn,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(f"Adding new group | Name: {group.name}")

    try:
        db_start = time.time()
        group_data = await create_group_record(supabase, group)
        db_duration = time.time() - db_start

        log_database_operation("insert", "groups", db_duration)
        track_database_operation("insert", "groups", db_duration)

        if not group_data:
            logger.error("Failed to create group record")
            raise HTTPException(500, ErrorMessages.ERROR_ADDING_GROUP)

        # Invalidate caches
        cache_key = GROUPS_ALL
        invalidate_cache(background_tasks, redis_client, cache_key)
        log_cache_operation("invalidate", cache_key)

        total_duration = time.time() - start_time
        logger.info(
            f"Group added successfully | ID: {group_data['id']} | Name: {group.name} | Total Duration: {total_duration:.3f}s"
        )

        return {"message": SuccessMessages.GROUP_ADDED, "group": group_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding group | Name: {group.name} | Error: {str(e)}")
        raise HTTPException(500, ErrorMessages.ERROR_ADDING_GROUP)


@router.delete("/{group_id}")
@expensive_rate_limit()
async def delete_group(
    group_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(f"Deleting group | ID: {group_id}")

    try:
        db_start = time.time()
        response = await delete_group_from_db(supabase, group_id)
        db_duration = time.time() - db_start

        log_database_operation("delete", "groups", db_duration)
        track_database_operation("delete", "groups", db_duration)

        if not response:
            logger.warning(f"Group not found | ID: {group_id}")
            raise HTTPException(404, ErrorMessages.GROUP_NOT_FOUND)

        # Invalidate multiple caches
        cache_keys_to_invalidate = [
            GROUPS_ALL,
            group_cache_key(group_id),
            group_expenses_cache_key(group_id),
            group_persons_cache_key(group_id),
            group_balances_cache_key(group_id),
        ]

        invalidate_multiple_caches(
            background_tasks, redis_client, cache_keys_to_invalidate
        )

        for cache_key in cache_keys_to_invalidate:
            log_cache_operation("invalidate", cache_key)

        total_duration = time.time() - start_time
        logger.info(
            f"Group deleted successfully | ID: {group_id} | Total Duration: {total_duration:.3f}s"
        )

        return {"message": SuccessMessages.GROUP_DELETED, "deleted_group": response}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting group | ID: {group_id} | Error: {str(e)}")
        raise HTTPException(status_code=500, detail=ErrorMessages.ERROR_DELETING_GROUP)


@router.put("/{group_id}")
@strict_rate_limit()
async def update_group(
    group_id: str,
    group: GroupUpdate,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(f"Updating group | ID: {group_id}")

    try:
        db_start = time.time()
        response = await update_group_in_db(supabase, group_id, group)
        db_duration = time.time() - db_start

        log_database_operation("update", "groups", db_duration)
        track_database_operation("update", "groups", db_duration)

        if not response:
            logger.warning(f"Group not found for update | ID: {group_id}")
            raise HTTPException(404, ErrorMessages.GROUP_NOT_FOUND)

        # Invalidate caches
        cache_keys_to_invalidate = [
            GROUPS_ALL,
            group_cache_key(group_id),
        ]

        invalidate_multiple_caches(
            background_tasks, redis_client, cache_keys_to_invalidate
        )

        for cache_key in cache_keys_to_invalidate:
            log_cache_operation("invalidate", cache_key)

        total_duration = time.time() - start_time
        logger.info(
            f"Group updated successfully | ID: {group_id} | Total Duration: {total_duration:.3f}s"
        )

        return {"message": SuccessMessages.GROUP_UPDATED, "group": response}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating group | ID: {group_id} | Error: {str(e)}")
        raise HTTPException(status_code=500, detail=ErrorMessages.ERROR_UPDATING_GROUP)


@router.get("/{group_id}/balances", response_model=GroupBalancesResponse)
@basic_rate_limit()
async def get_group_balances(
    group_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = group_balances_cache_key(group_id)
    start_time = time.time()

    logger.info(f"Fetching balances for group | ID: {group_id}")

    try:
        # Try to get from cache
        balances = await get_cached_single_object(redis_client, cache_key)

        if balances:
            log_cache_operation("get", cache_key, True)
            track_cache_operation("get", True)
            logger.info(f"Group balances retrieved from cache | Group: {group_id}")
        else:
            log_cache_operation("get", cache_key, False)
            track_cache_operation("get", False)

            # Calculate from database
            db_start = time.time()
            balances = await calculate_group_balances(supabase, group_id)
            db_duration = time.time() - db_start

            log_database_operation("calculate_balances", "expenses", db_duration)
            track_database_operation("calculate_balances", "expenses", db_duration)

            # Store as a single item list for cache consistency
            cache_single_object(
                background_tasks,
                redis_client,
                cache_key,
                balances,
            )
            log_cache_operation("set", cache_key)

            logger.info(
                f"Group balances calculated from database | Group: {group_id} | DB Duration: {db_duration:.3f}s"
            )

        total_duration = time.time() - start_time
        logger.info(
            f"Get group balances completed | Group: {group_id} | Total Duration: {total_duration:.3f}s"
        )

        return GroupBalancesResponse(balances=balances)

    except Exception as e:
        logger.error(
            f"Error fetching group balances | Group: {group_id} | Error: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail=ErrorMessages.ERROR_RETRIEVING_GROUP_BALANCES
        )
