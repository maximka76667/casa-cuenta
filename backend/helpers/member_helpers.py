from models.group_user import GroupUserIn, GroupUserUpdate


async def get_all_members_from_db(supabase):
    """Get all members from database"""
    return supabase.table("group_users").select("*").execute().data


async def create_member_record(supabase, member: GroupUserIn):
    """Create member record in database"""
    response = supabase.table("group_users").insert(member.model_dump()).execute()
    return response.data[0] if response.data else None


async def get_member_user_id(supabase, member_id: str):
    """Get user_id for specific member"""
    response = (
        supabase.table("group_users").select("user_id").eq("id", member_id).execute()
    )
    return response.data[0]["user_id"] if response.data else None


async def delete_member_from_db(supabase, member_id: str):
    """Delete member from database"""
    response = supabase.table("group_users").delete().eq("id", member_id).execute()
    return response.data


async def update_member_in_db(supabase, member_id: str, member: GroupUserUpdate):
    """Update member in database"""
    response = (
        supabase.table("group_users")
        .update(member.model_dump(exclude_unset=True))
        .eq("id", member_id)
        .execute()
    )
    return response.data
