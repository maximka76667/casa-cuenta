from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from models.user import UserGroupsResponse
from helpers.cache_helpers import get_cached_items, cache_items
from helpers.user_helpers import get_user_groups_from_db
from constants.cache_keys import user_groups_cache_key
from constants.api_messages import ErrorMessages

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/{user_id}/groups", response_model=UserGroupsResponse)
async def get_user_groups(
    user_id: str,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    try:
        cache_key = user_groups_cache_key(user_id)

        # Try to get from cache
        groups = await get_cached_items(redis_client, cache_key)

        # If not in cache, get from database and cache it
        if not groups:
            groups = await get_user_groups_from_db(supabase, user_id)
            if groups is None:
                raise HTTPException(404, ErrorMessages.USER_NOT_FOUND)
            cache_items(
                background_tasks, redis_client, cache_key, groups, id_field="id"
            )

        return UserGroupsResponse(groups=groups)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, ErrorMessages.ERROR_RETRIEVING_USER_GROUPS)
