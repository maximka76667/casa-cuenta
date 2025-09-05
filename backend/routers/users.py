from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
import time

# Models
from models.user import UserGroupsResponse

# Helpers
from helpers.cache_helpers import get_cached_items, cache_items
from helpers.user_helpers import get_user_groups_from_db

# Middlewares
from middlewares.rate_limiter import basic_rate_limit
from middlewares.logger import get_logger, log_cache_operation, log_database_operation
from middlewares.monitoring import track_cache_operation, track_database_operation

# Constants
from constants.cache_keys import user_groups_cache_key
from constants.api_messages import ErrorMessages

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

logger = get_logger()


@router.get("/{user_id}/groups", response_model=UserGroupsResponse)
@basic_rate_limit()
async def get_user_groups(
    user_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(f"Fetching groups for user | ID: {user_id}")

    try:
        cache_key = user_groups_cache_key(user_id)

        # Try to get from cache
        groups = await get_cached_items(redis_client, cache_key)

        if groups:
            log_cache_operation("get", cache_key, True)
            track_cache_operation("get", True)
            logger.info(
                f"User groups retrieved from cache | User: {user_id} | Count: {len(groups)}"
            )
        else:
            log_cache_operation("get", cache_key, False)
            track_cache_operation("get", False)

            # Get from database
            db_start = time.time()
            groups = await get_user_groups_from_db(supabase, user_id)
            db_duration = time.time() - db_start

            log_database_operation("select", "user_groups", db_duration)
            track_database_operation("select", "user_groups", db_duration)

            if groups is None:
                logger.warning(f"User not found | ID: {user_id}")
                raise HTTPException(404, ErrorMessages.USER_NOT_FOUND)

            # Cache the results
            cache_items(
                background_tasks, redis_client, cache_key, groups, id_field="id"
            )
            log_cache_operation("set", cache_key)

            logger.info(
                f"User groups retrieved from database | User: {user_id} | Count: {len(groups)} | DB Duration: {db_duration:.3f}s"
            )

        total_duration = time.time() - start_time
        logger.info(
            f"Get user groups completed | User: {user_id} | Total Duration: {total_duration:.3f}s"
        )

        return UserGroupsResponse(groups=groups)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving user groups | User: {user_id} | Error: {str(e)}"
        )
        raise HTTPException(500, ErrorMessages.ERROR_RETRIEVING_USER_GROUPS)
