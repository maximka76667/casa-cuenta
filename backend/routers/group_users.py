from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from models.group_user import GroupUserIn, GroupUserUpdate, GroupUsersListResponse
from helpers.cache_helpers import get_cached_items, cache_items, invalidate_cache
from helpers.member_helpers import (
    get_all_members_from_db,
    create_member_record,
    get_member_user_id,
    delete_member_from_db,
    update_member_in_db,
)
from constants.cache_keys import MEMBERS_ALL, user_groups_cache_key
from constants.api_messages import SuccessMessages, ErrorMessages

router = APIRouter(
    prefix="/members",
    tags=["members"],
)


@router.get("/", response_model=GroupUsersListResponse)
async def get_members(
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = MEMBERS_ALL

    # Try to get from cache
    members = await get_cached_items(redis_client, cache_key)

    # If not in cache, get from database and cache it
    if not members:
        members = await get_all_members_from_db(supabase)
        cache_items(background_tasks, redis_client, cache_key, members)

    return GroupUsersListResponse(members=members)


@router.post("/")
async def add_member(
    member: GroupUserIn,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    try:
        member_data = await create_member_record(supabase, member)
        if not member_data:
            raise HTTPException(500, ErrorMessages.ERROR_ADDING_MEMBER)

        # Invalidate caches
        global_cache_key = MEMBERS_ALL
        user_cache_key = user_groups_cache_key(member.user_id)
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        invalidate_cache(background_tasks, redis_client, user_cache_key)

        return {"message": SuccessMessages.MEMBER_ADDED, "member": member_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, ErrorMessages.ERROR_ADDING_MEMBER)


@router.delete("/{member_id}")
async def delete_member(
    member_id: str,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    try:
        # Get user_id before deletion
        user_id = await get_member_user_id(supabase, member_id)
        if user_id is None:
            raise HTTPException(404, ErrorMessages.MEMBER_NOT_FOUND)

        # Delete member
        response = await delete_member_from_db(supabase, member_id)
        if not response:
            raise HTTPException(404, ErrorMessages.MEMBER_NOT_FOUND)

        # Invalidate caches
        global_cache_key = MEMBERS_ALL
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        if user_id:
            user_cache_key = user_groups_cache_key(user_id)
            invalidate_cache(background_tasks, redis_client, user_cache_key)

        return {"message": SuccessMessages.MEMBER_DELETED, "deleted_member": response}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, ErrorMessages.ERROR_DELETING_MEMBER)


@router.put("/{member_id}")
async def update_member(
    member_id: str,
    member: GroupUserUpdate,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    try:
        # Get user_id for cache invalidation
        user_id = await get_member_user_id(supabase, member_id)
        if user_id is None:
            raise HTTPException(404, ErrorMessages.MEMBER_NOT_FOUND)

        # Update member
        response = await update_member_in_db(supabase, member_id, member)
        if not response:
            raise HTTPException(404, ErrorMessages.MEMBER_NOT_FOUND)

        # Invalidate caches
        global_cache_key = MEMBERS_ALL
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        if user_id:
            user_cache_key = user_groups_cache_key(user_id)
            invalidate_cache(background_tasks, redis_client, user_cache_key)

        return {"message": SuccessMessages.MEMBER_UPDATED, "member": response}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, ErrorMessages.ERROR_UPDATING_MEMBER)
