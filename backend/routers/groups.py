from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from models.expense import ExpenseListResponse
from models.group import GroupIn, GroupUpdate
from models.responses import (
    GroupListResponse,
    GroupResponse,
    GroupPersonsResponse,
    GroupBalancesResponse,
)
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
from constants.cache_keys import (
    GROUPS_ALL,
    group_cache_key,
    group_expenses_cache_key,
    group_persons_cache_key,
    group_balances_cache_key,
)
from constants.api_messages import SuccessMessages, ErrorMessages

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)


# Groups
@router.get("/", response_model=GroupListResponse)
async def get_groups(
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = GROUPS_ALL

    # Try to get from cache
    groups = await get_cached_items(redis_client, cache_key)

    # If not in cache, get from database and cache it
    if not groups:
        groups = await get_all_groups_from_db(supabase)
        cache_items(background_tasks, redis_client, cache_key, groups)

    return GroupListResponse(groups=groups)


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: str,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = group_cache_key(group_id)

    # Try to get from cache
    group = await get_cached_single_object(redis_client, cache_key)

    # If not in cache, get from database and cache it
    if not group:
        group = await get_group_by_id_from_db(supabase, group_id)
        cache_single_object(background_tasks, redis_client, cache_key, group)

    return GroupResponse(group=group)


@router.get("/{group_id}/expenses", response_model=ExpenseListResponse)
async def get_expenses_for_group(
    group_id: str,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = group_expenses_cache_key(group_id)

    # Try to get from cache
    expenses = await get_cached_items(redis_client, cache_key)

    # If not in cache, get from database and cache it
    if not expenses:
        expenses = await get_group_expenses_from_db(supabase, group_id)
        cache_items(background_tasks, redis_client, cache_key, expenses)

    return ExpenseListResponse(expenses=expenses)


@router.get("/{group_id}/persons", response_model=GroupPersonsResponse)
async def get_group_persons(
    group_id: str,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = group_persons_cache_key(group_id)

    # Try to get from cache
    persons = await get_cached_items(redis_client, cache_key)

    # If not in cache, get from database and cache it
    if not persons:
        persons = await get_group_persons_from_db(supabase, group_id)
        cache_items(background_tasks, redis_client, cache_key, persons)

    return GroupPersonsResponse(persons=persons)


@router.post("/")
async def add_group(
    group: GroupIn,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    try:
        group_data = await create_group_record(supabase, group)
        if not group_data:
            raise HTTPException(500, ErrorMessages.ERROR_ADDING_GROUP)

        # Invalidate caches
        cache_key = GROUPS_ALL
        invalidate_cache(background_tasks, redis_client, cache_key)

        return {"message": SuccessMessages.GROUP_ADDED, "group": group_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, ErrorMessages.ERROR_ADDING_GROUP)


@router.delete("/{group_id}")
async def delete_group(
    group_id: str,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    try:
        response = await delete_group_from_db(supabase, group_id)
        if not response.data:
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

        return {"message": SuccessMessages.GROUP_DELETED, "deleted_group": response}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorMessages.ERROR_DELETING_GROUP)


@router.put("/{group_id}")
async def update_group(
    group_id: str,
    group: GroupUpdate,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    try:
        response = await update_group_in_db(supabase, group_id, group)
        if not response.data:
            raise HTTPException(404, ErrorMessages.GROUP_NOT_FOUND)

        # Invalidate caches
        cache_keys_to_invalidate = [
            GROUPS_ALL,
            group_cache_key(group_id),
        ]
        invalidate_multiple_caches(
            background_tasks, redis_client, cache_keys_to_invalidate
        )

        return {"message": SuccessMessages.GROUP_UPDATED, "group": response.data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorMessages.ERROR_UPDATING_GROUP)


@router.get("/{group_id}/balances", response_model=GroupBalancesResponse)
async def get_group_balances(
    group_id: str,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = group_balances_cache_key(group_id)

    # Try to get from cache
    balances = await get_cached_single_object(redis_client, cache_key)

    # If not in cache, calculate from database and cache it
    if not balances:
        balances = await calculate_group_balances(supabase, group_id)
        # Store as a single item list for cache consistency
        cache_single_object(
            background_tasks,
            redis_client,
            cache_key,
            balances,
        )

    return GroupBalancesResponse(balances=balances)
