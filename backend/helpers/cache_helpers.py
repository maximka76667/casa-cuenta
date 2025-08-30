import json
from typing import List, Dict, Any, Optional
from datetime import datetime, date


def serialize_dates(v):
    return v.isoformat() if isinstance(v, datetime) else v


def datetime_parser(dct):
    for k, v in dct.items():
        if isinstance(v, str) and v.endswith("+00:00"):
            try:
                dct[k] = datetime.fromisoformat(v)
            except:
                pass
    return dct


async def cache_single_object_async(redis_client, cache_key: str, data: Dict):
    """Cache a single object directly (not as part of a hash)"""
    data_json = json.dumps(data, default=serialize_dates)
    await redis_client.set(cache_key, data_json)


async def get_cached_single_object_async(
    redis_client, cache_key: str
) -> Optional[Dict]:
    """Get a single cached object"""
    data = await redis_client.get(cache_key)
    if data:
        return json.loads(data, object_hook=datetime_parser)
    return None


def cache_single_object(background_tasks, redis_client, cache_key: str, data: Dict):
    """Cache a single object using background tasks"""
    background_tasks.add_task(cache_single_object_async, redis_client, cache_key, data)


async def get_cached_single_object(redis_client, cache_key: str) -> Optional[Dict]:
    """Get a single cached object (for use in routes)"""
    return await get_cached_single_object_async(redis_client, cache_key)


async def get_cached_items_async(redis_client, cache_key: str):
    return await redis_client.hgetall(cache_key)


async def cache_item_async(redis_client, cache_key: str, item_id: str, item_json: str):
    await redis_client.hset(cache_key, item_id, item_json)


async def delete_cache_item_async(redis_client, cache_key: str, item_id: str):
    await redis_client.hdel(cache_key, item_id)


async def delete_cache_key_async(redis_client, cache_key: str):
    """Delete entire cache key"""
    await redis_client.delete(cache_key)


# Generic cache functions
async def get_cached_items(redis_client, cache_key: str) -> Optional[List[Dict]]:
    """Generic function to get items from cache"""
    data = await get_cached_items_async(redis_client, cache_key)
    if data:
        return [json.loads(v, object_hook=datetime_parser) for v in data.values()]
    return None


def cache_items(
    background_tasks,
    redis_client,
    cache_key: str,
    items: List[Dict],
    id_field: str = "id",
):
    """Generic function to cache list of items"""

    for item in items:

        item_json = json.dumps(item, default=serialize_dates)
        print(f"Set {item_json}")

        background_tasks.add_task(
            cache_item_async, redis_client, cache_key, item[id_field], item_json
        )


def update_item_cache(
    background_tasks,
    redis_client,
    cache_key: str,
    item_data: Dict,
    id_field: str = "id",
):
    """Generic function to update single item in cache"""
    item_id = item_data[id_field]
    item_json = json.dumps(item_data, default=serialize_dates)
    print(f"Update {item_json}")
    background_tasks.add_task(
        cache_item_async, redis_client, cache_key, item_id, item_json
    )


def remove_item_from_cache(
    background_tasks, redis_client, cache_key: str, item_id: str
):
    """Generic function to remove item from cache"""
    background_tasks.add_task(delete_cache_item_async, redis_client, cache_key, item_id)


def invalidate_cache(background_tasks, redis_client, cache_key: str):
    """Generic function to invalidate/delete entire cache key"""
    background_tasks.add_task(delete_cache_key_async, redis_client, cache_key)


def invalidate_multiple_caches(background_tasks, redis_client, cache_keys: List[str]):
    """Generic function to invalidate multiple cache keys"""
    for cache_key in cache_keys:
        background_tasks.add_task(delete_cache_key_async, redis_client, cache_key)
