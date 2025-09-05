from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
import time

# Models
from models.group_user import GroupUserIn, GroupUserUpdate, GroupUsersListResponse

# Helpers
from helpers.cache_helpers import get_cached_items, cache_items, invalidate_cache
from helpers.member_helpers import (
    get_all_members_from_db,
    create_member_record,
    get_member_user_id,
    delete_member_from_db,
    update_member_in_db,
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
from constants.cache_keys import MEMBERS_ALL, user_groups_cache_key
from constants.api_messages import SuccessMessages, ErrorMessages

router = APIRouter(
    prefix="/members",
    tags=["members"],
)

logger = get_logger()


@router.get("/", response_model=GroupUsersListResponse)
@basic_rate_limit()
async def get_members(
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = MEMBERS_ALL
    start_time = time.time()

    logger.info("Fetching all members")

    try:
        # Try to get from cache
        members = await get_cached_items(redis_client, cache_key)

        if members:
            log_cache_operation("get", cache_key, True)
            track_cache_operation("get", True)
            logger.info(f"Members retrieved from cache | Count: {len(members)}")
        else:
            log_cache_operation("get", cache_key, False)
            track_cache_operation("get", False)

            # Get from database
            db_start = time.time()
            members = await get_all_members_from_db(supabase)
            db_duration = time.time() - db_start

            log_database_operation("select", "members", db_duration)
            track_database_operation("select", "members", db_duration)

            # Cache the results
            cache_items(background_tasks, redis_client, cache_key, members)
            log_cache_operation("set", cache_key)

            logger.info(
                f"Members retrieved from database | Count: {len(members)} | DB Duration: {db_duration:.3f}s"
            )

        total_duration = time.time() - start_time
        logger.info(f"Get members completed | Total Duration: {total_duration:.3f}s")

        return GroupUsersListResponse(members=members)

    except Exception as e:
        logger.error(f"Error fetching members: {str(e)}")
        raise HTTPException(
            status_code=500, detail=ErrorMessages.ERROR_RETRIEVING_MEMBERS
        )


@router.post("/")
@strict_rate_limit()
async def add_member(
    member: GroupUserIn,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(
        f"Adding new member | User: {member.user_id} | Group: {member.group_id}"
    )

    try:
        db_start = time.time()
        member_data = await create_member_record(supabase, member)
        db_duration = time.time() - db_start

        log_database_operation("insert", "members", db_duration)
        track_database_operation("insert", "members", db_duration)

        if not member_data:
            logger.error("Failed to create member record")
            raise HTTPException(500, ErrorMessages.ERROR_ADDING_MEMBER)

        # Invalidate caches
        global_cache_key = MEMBERS_ALL
        user_cache_key = user_groups_cache_key(member.user_id)

        invalidate_cache(background_tasks, redis_client, global_cache_key)
        invalidate_cache(background_tasks, redis_client, user_cache_key)

        log_cache_operation("invalidate", global_cache_key)
        log_cache_operation("invalidate", user_cache_key)

        total_duration = time.time() - start_time
        logger.info(
            f"Member added successfully | ID: {member_data['id']} | User: {member.user_id} | Group: {member.group_id} | Total Duration: {total_duration:.3f}s"
        )

        return {"message": SuccessMessages.MEMBER_ADDED, "member": member_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error adding member | User: {member.user_id} | Group: {member.group_id} | Error: {str(e)}"
        )
        raise HTTPException(500, ErrorMessages.ERROR_ADDING_MEMBER)


@router.delete("/{member_id}")
@expensive_rate_limit()
async def delete_member(
    member_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(f"Deleting member | ID: {member_id}")

    try:
        # Get user_id before deletion
        db_start = time.time()
        user_id = await get_member_user_id(supabase, member_id)
        db_duration = time.time() - db_start

        log_database_operation("select", "members", db_duration)
        track_database_operation("select", "members", db_duration)

        if user_id is None:
            logger.warning(f"Member not found | ID: {member_id}")
            raise HTTPException(404, ErrorMessages.MEMBER_NOT_FOUND)

        # Delete member
        db_start = time.time()
        response = await delete_member_from_db(supabase, member_id)
        db_duration = time.time() - db_start

        log_database_operation("delete", "members", db_duration)
        track_database_operation("delete", "members", db_duration)

        if not response:
            logger.warning(f"Member deletion failed | ID: {member_id}")
            raise HTTPException(404, ErrorMessages.MEMBER_NOT_FOUND)

        # Invalidate caches
        global_cache_key = MEMBERS_ALL
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        log_cache_operation("invalidate", global_cache_key)

        if user_id:
            user_cache_key = user_groups_cache_key(user_id)
            invalidate_cache(background_tasks, redis_client, user_cache_key)
            log_cache_operation("invalidate", user_cache_key)

        total_duration = time.time() - start_time
        logger.info(
            f"Member deleted successfully | ID: {member_id} | Total Duration: {total_duration:.3f}s"
        )

        return {"message": SuccessMessages.MEMBER_DELETED, "deleted_member": response}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting member | ID: {member_id} | Error: {str(e)}")
        raise HTTPException(500, ErrorMessages.ERROR_DELETING_MEMBER)


@router.put("/{member_id}")
@strict_rate_limit()
async def update_member(
    member_id: str,
    member: GroupUserUpdate,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(f"Updating member | ID: {member_id}")

    try:
        # Get user_id for cache invalidation
        db_start = time.time()
        user_id = await get_member_user_id(supabase, member_id)
        db_duration = time.time() - db_start

        log_database_operation("select", "members", db_duration)
        track_database_operation("select", "members", db_duration)

        if user_id is None:
            logger.warning(f"Member not found for update | ID: {member_id}")
            raise HTTPException(404, ErrorMessages.MEMBER_NOT_FOUND)

        # Update member
        db_start = time.time()
        response = await update_member_in_db(supabase, member_id, member)
        db_duration = time.time() - db_start

        log_database_operation("update", "members", db_duration)
        track_database_operation("update", "members", db_duration)

        if not response:
            logger.warning(f"Member update failed | ID: {member_id}")
            raise HTTPException(404, ErrorMessages.MEMBER_NOT_FOUND)

        # Invalidate caches
        global_cache_key = MEMBERS_ALL
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        log_cache_operation("invalidate", global_cache_key)

        if user_id:
            user_cache_key = user_groups_cache_key(user_id)
            invalidate_cache(background_tasks, redis_client, user_cache_key)
            log_cache_operation("invalidate", user_cache_key)

        total_duration = time.time() - start_time
        logger.info(
            f"Member updated successfully | ID: {member_id} | Total Duration: {total_duration:.3f}s"
        )

        return {"message": SuccessMessages.MEMBER_UPDATED, "member": response}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating member | ID: {member_id} | Error: {str(e)}")
        raise HTTPException(500, ErrorMessages.ERROR_UPDATING_MEMBER)
