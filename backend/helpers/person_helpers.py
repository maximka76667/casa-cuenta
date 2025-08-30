from models.person import PersonIn, PersonUpdate


async def get_all_persons_from_db(supabase):
    """Get all persons from database"""
    return supabase.table("persons").select("*").execute().data


async def create_person_record(supabase, person: PersonIn):
    """Create person record in database"""
    response = supabase.table("persons").insert(person.model_dump()).execute()
    return response.data[0] if response.data else None


async def get_person_group_id(supabase, person_id: str):
    """Get group_id for specific person"""
    response = (
        supabase.table("persons").select("group_id").eq("id", person_id).execute()
    )
    return response.data[0]["group_id"] if response.data else None


async def delete_person_from_db(supabase, person_id: str):
    """Delete person from database"""
    response = supabase.table("persons").delete().eq("id", person_id).execute()
    return response.data[0] if response.data else None


async def update_person_in_db(supabase, person_id: str, person: PersonUpdate):
    """Update person in database"""
    response = (
        supabase.table("persons")
        .update(person.model_dump())
        .eq("id", person_id)
        .execute()
    )
    return response.data
