async def get_user_groups_from_db(supabase, user_id: str):
    """Get groups for specific user from database"""
    response = (
        supabase.table("group_users")
        .select("group:groups(id, name, created_at)")
        .eq("user_id", user_id)
        .execute()
    )
    return [g["group"] for g in response.data]

