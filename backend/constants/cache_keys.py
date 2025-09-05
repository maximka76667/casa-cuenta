# Cache key constants and generators

# Global cache keys
EXPENSES_ALL = "expenses:all"
GROUPS_ALL = "groups:all"
PERSONS_ALL = "persons:all"
DEBTORS_ALL = "debtors:all"
MEMBERS_ALL = "members:all"


# Dynamic cache key generators
def group_cache_key(group_id: str) -> str:
    """Generate cache key for a specific group"""
    return f"groups:{group_id}"


def group_expenses_cache_key(group_id: str) -> str:
    """Generate cache key for expenses of a specific group"""
    return f"groups:{group_id}:expenses"


def group_persons_cache_key(group_id: str) -> str:
    """Generate cache key for persons in a specific group"""
    return f"groups:{group_id}:persons"


def group_debtors_cache_key(group_id: str) -> str:
    """Generate cache key for debtors in a specific group"""
    return f"groups:{group_id}:debtors"


def group_balances_cache_key(group_id: str) -> str:
    """Generate cache key for balances of a specific group"""
    return f"groups:{group_id}:balances"


def user_groups_cache_key(user_id: str) -> str:
    """Generate cache key for groups of a specific user"""
    return f"users:{user_id}:groups"


