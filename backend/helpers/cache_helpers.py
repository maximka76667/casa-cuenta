import json
from typing import List, Dict, Any, Optional


# Generic cache functions
async def get_cached_items(redis_client, cache_key: str) -> Optional[List[Dict]]:
    """Generic function to get items from cache"""
    data = await redis_client.hgetall(cache_key)
    if data:
        return [json.loads(v) for v in data.values()]
    return None


async def cache_items(
    background_tasks,
    redis_client,
    cache_key: str,
    items: List[Dict],
    id_field: str = "id",
):
    """Generic function to cache list of items"""
    for item in items:
        background_tasks.add_task(
            redis_client.hset, cache_key, item[id_field], json.dumps(item)
        )


async def update_item_cache(
    background_tasks,
    redis_client,
    cache_key: str,
    item_data: Dict,
    id_field: str = "id",
):
    """Generic function to update single item in cache"""
    item_id = item_data[id_field]
    item_json = json.dumps(item_data)
    background_tasks.add_task(redis_client.hset, cache_key, item_id, item_json)


async def remove_item_from_cache(
    background_tasks, redis_client, cache_key: str, item_id: str
):
    """Generic function to remove item from cache"""
    background_tasks.add_task(redis_client.hdel, cache_key, item_id)


# Specific expense cache functions built on top of generic ones
async def get_cached_expenses(redis_client, cache_key: str) -> Optional[List[Dict]]:
    """Get expenses from cache"""
    return await get_cached_items(redis_client, cache_key)


async def cache_expenses(
    background_tasks, redis_client, cache_key: str, expenses: List[Dict]
):
    """Cache list of expenses"""
    await cache_items(background_tasks, redis_client, cache_key, expenses)


async def update_expense_cache(
    background_tasks, redis_client, expense_data: Dict, group_id: str
):
    """Update expense in multiple cache locations"""
    expense_id = expense_data["id"]

    # Update in global cache
    await update_item_cache(
        background_tasks, redis_client, "expenses:all", expense_data
    )

    # Update in group cache
    await update_item_cache(
        background_tasks, redis_client, f"groups:{group_id}:expenses", expense_data
    )


async def remove_expense_from_cache(
    background_tasks, redis_client, expense_id: str, group_id: str = None
):
    """Remove expense from multiple cache locations"""
    # Remove from global cache
    await remove_item_from_cache(
        background_tasks, redis_client, "expenses:all", expense_id
    )

    # Remove from group cache
    if group_id:
        await remove_item_from_cache(
            background_tasks, redis_client, f"groups:{group_id}:expenses", expense_id
        )


# Example: You can now easily create cache functions for other entities
async def get_cached_groups(redis_client, cache_key: str) -> Optional[List[Dict]]:
    """Get groups from cache"""
    return await get_cached_items(redis_client, cache_key)


async def cache_groups(
    background_tasks, redis_client, cache_key: str, groups: List[Dict]
):
    """Cache list of groups"""
    await cache_items(background_tasks, redis_client, cache_key, groups)


async def update_group_cache(
    background_tasks, redis_client, cache_key: str, group_data: Dict
):
    """Update single group in cache"""
    await update_item_cache(background_tasks, redis_client, cache_key, group_data)


async def remove_group_from_cache(
    background_tasks, redis_client, cache_key: str, group_id: str
):
    """Remove group from cache"""
    await remove_item_from_cache(background_tasks, redis_client, cache_key, group_id)
