from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from models.person import PersonIn, PersonUpdate, PersonListResponse
from helpers.cache_helpers import get_cached_items, cache_items, invalidate_cache
from helpers.person_helpers import (
    get_all_persons_from_db,
    create_person_record,
    get_person_group_id,
    delete_person_from_db,
    update_person_in_db,
)
from constants.cache_keys import (
    PERSONS_ALL,
    group_persons_cache_key,
    group_balances_cache_key,
)
from constants.api_messages import SuccessMessages, ErrorMessages

router = APIRouter(
    prefix="/persons",
    tags=["persons"],
)


@router.get("/", response_model=PersonListResponse)
async def get_persons(
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = PERSONS_ALL

    # Try to get from cache
    persons = await get_cached_items(redis_client, cache_key)

    # If not in cache, get from database and cache it
    if not persons:
        persons = await get_all_persons_from_db(supabase)
        cache_items(background_tasks, redis_client, cache_key, persons)

    return PersonListResponse(persons=persons)


@router.post("/")
async def add_person(
    person: PersonIn,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    try:
        person_data = await create_person_record(supabase, person)
        if not person_data:
            raise HTTPException(500, ErrorMessages.ERROR_ADDING_PERSON)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, ErrorMessages.ERROR_ADDING_PERSON)

    # Invalidate caches
    global_cache_key = PERSONS_ALL
    persons_cache_key = group_persons_cache_key(person.group_id)
    balances_cache_key = group_balances_cache_key(person.group_id)

    invalidate_cache(background_tasks, redis_client, global_cache_key)
    invalidate_cache(background_tasks, redis_client, persons_cache_key)
    invalidate_cache(background_tasks, redis_client, balances_cache_key)

    return {"message": SuccessMessages.PERSON_ADDED, "person": person_data}


@router.delete("/{person_id}")
async def delete_person(
    person_id: str,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    # Get group_id before deletion
    group_id = await get_person_group_id(supabase, person_id)
    if group_id is None:
        raise HTTPException(404, ErrorMessages.PERSON_NOT_FOUND)

    try:
        data = await delete_person_from_db(supabase, person_id)
        print(data)
        if not data:
            raise HTTPException(404, ErrorMessages.PERSON_NOT_FOUND)

        # Invalidate caches
        global_cache_key = PERSONS_ALL
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        if group_id:
            group_cache_key = group_persons_cache_key(group_id)
            invalidate_cache(background_tasks, redis_client, group_cache_key)

        return {"message": SuccessMessages.PERSON_DELETED, "deleted_person": data}
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(500, ErrorMessages.ERROR_DELETING_PERSON)


@router.put("/{person_id}")
async def update_person(
    person_id: str,
    person: PersonUpdate,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    try:
        # Get group_id for cache invalidation
        group_id = await get_person_group_id(supabase, person_id)
        if group_id is None:
            raise HTTPException(404, ErrorMessages.PERSON_NOT_FOUND)

        # Update person
        response = await update_person_in_db(supabase, person_id, person)
        if not response:
            raise HTTPException(404, ErrorMessages.PERSON_NOT_FOUND)

        # Invalidate caches
        global_cache_key = PERSONS_ALL
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        if group_id:
            group_cache_key = group_persons_cache_key(group_id)
            invalidate_cache(background_tasks, redis_client, group_cache_key)

        return {"message": SuccessMessages.PERSON_UPDATED, "person": response}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, ErrorMessages.ERROR_UPDATING_PERSON)
