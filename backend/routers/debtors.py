from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from models.debtor import ExpenseDebtorIn, ExpenseDebtorUpdate, DebtorListResponse
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
from constants.cache_keys import DEBTORS_ALL, group_debtors_cache_key
from constants.api_messages import SuccessMessages, ErrorMessages

router = APIRouter(
    prefix="/debtors",
    tags=["debtors"],
)


@router.get("/", response_model=DebtorListResponse)
async def get_debtors(
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = DEBTORS_ALL

    # Try to get from cache
    debtors = await get_cached_items(redis_client, cache_key)

    # If not in cache, get from database and cache it
    if not debtors:
        debtors = await get_all_debtors_from_db(supabase)
        cache_items(background_tasks, redis_client, cache_key, debtors)

    return DebtorListResponse(debtors=debtors)


@router.get("/{group_id}", response_model=DebtorListResponse)
async def get_debtors_for_group(
    group_id: str,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = group_debtors_cache_key(group_id)

    # Try to get from cache
    debtors = await get_cached_items(redis_client, cache_key)

    # If not in cache, get from database and cache it
    if not debtors:
        debtors = await get_group_debtors_from_db(supabase, group_id)
        cache_items(background_tasks, redis_client, cache_key, debtors)

    return DebtorListResponse(debtors=debtors)


@router.post("/")
async def add_debtor(
    debtor: ExpenseDebtorIn,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    try:
        # Get group_id for cache invalidation
        group_id = await get_expense_group_id_from_expense(supabase, debtor.expense_id)

        debtor_data = await create_debtor_record(supabase, debtor)
        if not debtor_data:
            raise HTTPException(500, ErrorMessages.ERROR_ADDING_DEBTOR)

        # Invalidate caches
        global_cache_key = DEBTORS_ALL
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        if group_id:
            group_cache_key = group_debtors_cache_key(group_id)
            invalidate_cache(background_tasks, redis_client, group_cache_key)

        return {"message": SuccessMessages.DEBTOR_ADDED, "debtor": debtor_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, ErrorMessages.ERROR_ADDING_DEBTOR)


@router.delete("/{debtor_id}")
async def delete_debtor(
    debtor_id: str,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    try:
        # Get expense_id and group_id for cache invalidation
        expense_id = await get_debtor_expense_id(supabase, debtor_id)
        if expense_id is None:
            raise HTTPException(404, ErrorMessages.DEBTOR_NOT_FOUND)

        group_id = await get_expense_group_id_from_expense(supabase, expense_id)

        # Delete debtor
        response = await delete_debtor_from_db(supabase, debtor_id)
        if not response:
            raise HTTPException(404, ErrorMessages.DEBTOR_NOT_FOUND)

        # Invalidate caches
        global_cache_key = DEBTORS_ALL
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        if group_id:
            group_cache_key = group_debtors_cache_key(group_id)
            invalidate_cache(background_tasks, redis_client, group_cache_key)

        return {"message": SuccessMessages.DEBTOR_DELETED, "deleted_debtor": response}
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(500, ErrorMessages.ERROR_DELETING_DEBTOR)


@router.put("/{debtor_id}")
async def update_debtor(
    debtor_id: str,
    debtor: ExpenseDebtorUpdate,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    try:
        # Get expense_id and group_id for cache invalidation
        expense_id = await get_debtor_expense_id(supabase, debtor_id)
        if expense_id is None:
            raise HTTPException(404, ErrorMessages.DEBTOR_NOT_FOUND)

        group_id = await get_expense_group_id_from_expense(supabase, expense_id)

        # Update debtor
        response = await update_debtor_in_db(supabase, debtor_id, debtor)
        if not response:
            raise HTTPException(404, ErrorMessages.DEBTOR_NOT_FOUND)

        # Invalidate caches
        global_cache_key = DEBTORS_ALL
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        if group_id:
            group_cache_key = group_debtors_cache_key(group_id)
            invalidate_cache(background_tasks, redis_client, group_cache_key)

        return {"message": SuccessMessages.DEBTOR_UPDATED, "debtor": response}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, ErrorMessages.ERROR_UPDATING_DEBTOR)
