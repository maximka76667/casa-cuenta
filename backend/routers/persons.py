from dependencies import get_redis, get_supabase
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
import time

# Models
from models.person import PersonIn, PersonUpdate, PersonListResponse

# Helpers
from helpers.cache_helpers import get_cached_items, cache_items, invalidate_cache
from helpers.person_helpers import (
    get_all_persons_from_db,
    create_person_record,
    get_person_group_id,
    delete_person_from_db,
    update_person_in_db,
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
    PERSONS_ALL,
    group_persons_cache_key,
    group_balances_cache_key,
)
from constants.api_messages import SuccessMessages, ErrorMessages

router = APIRouter(
    prefix="/persons",
    tags=["persons"],
)

logger = get_logger()


@router.get("/", response_model=PersonListResponse)
@basic_rate_limit()
async def get_persons(
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    cache_key = PERSONS_ALL
    start_time = time.time()

    logger.info("Fetching all persons")

    try:
        # Try to get from cache
        persons = await get_cached_items(redis_client, cache_key)

        if persons:
            log_cache_operation("get", cache_key, True)
            track_cache_operation("get", True)
            logger.info(f"Persons retrieved from cache | Count: {len(persons)}")
        else:
            log_cache_operation("get", cache_key, False)
            track_cache_operation("get", False)

            # Get from database
            db_start = time.time()
            persons = await get_all_persons_from_db(supabase)
            db_duration = time.time() - db_start

            log_database_operation("select", "persons", db_duration)
            track_database_operation("select", "persons", db_duration)

            # Cache the results
            cache_items(background_tasks, redis_client, cache_key, persons)
            log_cache_operation("set", cache_key)

            logger.info(
                f"Persons retrieved from database | Count: {len(persons)} | DB Duration: {db_duration:.3f}s"
            )

        total_duration = time.time() - start_time
        logger.info(f"Get persons completed | Total Duration: {total_duration:.3f}s")

        return PersonListResponse(persons=persons)

    except Exception as e:
        logger.error(f"Error fetching persons: {str(e)}")
        raise HTTPException(
            status_code=500, detail=ErrorMessages.ERROR_RETRIEVING_PERSONS
        )


@router.post("/")
@strict_rate_limit()
async def add_person(
    person: PersonIn,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(f"Adding new person | Name: {person.name} | Group: {person.group_id}")

    try:
        db_start = time.time()
        person_data = await create_person_record(supabase, person)
        db_duration = time.time() - db_start

        log_database_operation("insert", "persons", db_duration)
        track_database_operation("insert", "persons", db_duration)

        if not person_data:
            logger.error("Failed to create person record")
            raise HTTPException(500, ErrorMessages.ERROR_ADDING_PERSON)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding person | Name: {person.name} | Error: {str(e)}")
        raise HTTPException(500, ErrorMessages.ERROR_ADDING_PERSON)

    # Invalidate caches
    global_cache_key = PERSONS_ALL
    persons_cache_key = group_persons_cache_key(person.group_id)
    balances_cache_key = group_balances_cache_key(person.group_id)

    invalidate_cache(background_tasks, redis_client, global_cache_key)
    invalidate_cache(background_tasks, redis_client, persons_cache_key)
    invalidate_cache(background_tasks, redis_client, balances_cache_key)

    log_cache_operation("invalidate", global_cache_key)
    log_cache_operation("invalidate", persons_cache_key)
    log_cache_operation("invalidate", balances_cache_key)

    total_duration = time.time() - start_time
    logger.info(
        f"Person added successfully | ID: {person_data['id']} | Name: {person.name} | Total Duration: {total_duration:.3f}s"
    )

    return {"message": SuccessMessages.PERSON_ADDED, "person": person_data}


@router.delete("/{person_id}")
@expensive_rate_limit()
async def delete_person(
    person_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(f"Deleting person | ID: {person_id}")

    # Get group_id before deletion
    db_start = time.time()
    group_id = await get_person_group_id(supabase, person_id)
    db_duration = time.time() - db_start

    log_database_operation("select", "persons", db_duration)
    track_database_operation("select", "persons", db_duration)

    if group_id is None:
        logger.warning(f"Person not found | ID: {person_id}")
        raise HTTPException(404, ErrorMessages.PERSON_NOT_FOUND)

    try:
        db_start = time.time()
        data = await delete_person_from_db(supabase, person_id)
        db_duration = time.time() - db_start

        log_database_operation("delete", "persons", db_duration)
        track_database_operation("delete", "persons", db_duration)

        if not data:
            logger.warning(f"Person deletion failed | ID: {person_id}")
            raise HTTPException(404, ErrorMessages.PERSON_NOT_FOUND)

        # Invalidate caches
        global_cache_key = PERSONS_ALL
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        log_cache_operation("invalidate", global_cache_key)

        if group_id:
            group_cache_key = group_persons_cache_key(group_id)
            invalidate_cache(background_tasks, redis_client, group_cache_key)
            log_cache_operation("invalidate", group_cache_key)

        total_duration = time.time() - start_time
        logger.info(
            f"Person deleted successfully | ID: {person_id} | Total Duration: {total_duration:.3f}s"
        )

        return {"message": SuccessMessages.PERSON_DELETED, "deleted_person": data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting person | ID: {person_id} | Error: {str(e)}")
        raise HTTPException(500, ErrorMessages.ERROR_DELETING_PERSON)


@router.put("/{person_id}")
@strict_rate_limit()
async def update_person(
    person_id: str,
    person: PersonUpdate,
    request: Request,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    start_time = time.time()
    logger.info(f"Updating person | ID: {person_id}")

    try:
        # Get group_id for cache invalidation
        db_start = time.time()
        group_id = await get_person_group_id(supabase, person_id)
        db_duration = time.time() - db_start

        log_database_operation("select", "persons", db_duration)
        track_database_operation("select", "persons", db_duration)

        if group_id is None:
            logger.warning(f"Person not found for update | ID: {person_id}")
            raise HTTPException(404, ErrorMessages.PERSON_NOT_FOUND)

        # Update person
        db_start = time.time()
        response = await update_person_in_db(supabase, person_id, person)
        db_duration = time.time() - db_start

        log_database_operation("update", "persons", db_duration)
        track_database_operation("update", "persons", db_duration)

        if not response:
            logger.warning(f"Person update failed | ID: {person_id}")
            raise HTTPException(404, ErrorMessages.PERSON_NOT_FOUND)

        # Invalidate caches
        global_cache_key = PERSONS_ALL
        invalidate_cache(background_tasks, redis_client, global_cache_key)
        log_cache_operation("invalidate", global_cache_key)

        if group_id:
            group_cache_key = group_persons_cache_key(group_id)
            invalidate_cache(background_tasks, redis_client, group_cache_key)
            log_cache_operation("invalidate", group_cache_key)

        total_duration = time.time() - start_time
        logger.info(
            f"Person updated successfully | ID: {person_id} | Total Duration: {total_duration:.3f}s"
        )

        return {"message": SuccessMessages.PERSON_UPDATED, "person": response}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating person | ID: {person_id} | Error: {str(e)}")
        raise HTTPException(500, ErrorMessages.ERROR_UPDATING_PERSON)
