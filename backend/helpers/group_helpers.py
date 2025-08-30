from models.group import GroupIn, GroupUpdate
from fastapi import HTTPException


async def get_all_groups_from_db(supabase):
    """Get all groups from database"""
    return supabase.table("groups").select("*").execute().data


async def get_group_by_id_from_db(supabase, group_id: str):
    """Get single group by ID from database"""
    response = (
        supabase.table("groups").select("*").eq("id", group_id).single().execute()
    )
    return response.data


async def get_group_persons_from_db(supabase, group_id: str):
    """Get persons for specific group from database"""
    return supabase.table("persons").select("*").eq("group_id", group_id).execute().data


async def create_group_record(supabase, group: GroupIn):
    """Create group record in database"""
    response = supabase.table("groups").insert(group.model_dump()).execute()
    return response.data[0] if response.data else None


async def delete_group_from_db(supabase, group_id: str):
    """Delete group from database"""
    response = supabase.table("groups").delete().eq("id", group_id).execute()
    return response.data


async def update_group_in_db(supabase, group_id: str, group: GroupUpdate):
    """Update group in database"""
    response = (
        supabase.table("groups").update(group.model_dump()).eq("id", group_id).execute()
    )
    return response.data


async def calculate_group_balances(supabase, group_id: str):
    """Calculate balances for all persons in a group"""
    # 1. Verify group exists
    group = supabase.table("groups").select("id").eq("id", group_id).single().execute()
    if not group.data:
        raise HTTPException(status_code=404, detail="Group not found")

    # 2. Get persons in group
    persons = (
        supabase.table("persons")
        .select("id, name")
        .eq("group_id", group_id)
        .execute()
        .data
    )
    if not persons:
        return {}

    balances = {
        person["id"]: {
            "name": person["name"],
            "paid": 0.0,
            "owes": 0.0,
            "balance": 0.0,
        }
        for person in persons
    }

    # 3. Get all expenses for this group
    expenses = (
        supabase.table("expenses")
        .select("id, amount, payer_id")
        .eq("group_id", group_id)
        .execute()
        .data
    )
    expense_ids = [e["id"] for e in expenses]

    # 4. Aggregate "paid" by payer
    for e in expenses:
        payer_id = e["payer_id"]
        if payer_id in balances:
            balances[payer_id]["paid"] += float(e["amount"])

    # 5. Get debtors only for this group's expenses
    if expense_ids:
        debtors = (
            supabase.table("expenses_debtors")
            .select("person_id, amount, expense_id")
            .in_("expense_id", expense_ids)
            .execute()
            .data
        )

        for d in debtors:
            if d["person_id"] in balances:
                balances[d["person_id"]]["owes"] += float(d["amount"])

    # 6. Compute net balance
    for person_id, data in balances.items():
        data["balance"] = data["paid"] - data["owes"]

    return balances

