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
    return response.data[0] if response.data else None


async def update_group_in_db(supabase, group_id: str, group: GroupUpdate):
    """Update group in database"""
    response = (
        supabase.table("groups")
        .update(group.model_dump(exclude_unset=True))
        .eq("id", group_id)
        .execute()
    )
    return response.data[0] if response.data else None


def calculate_debtor_amount(debtor: dict, expense_amount: float, all_debtors: list) -> float:
    """Calculate actual dollar amount for a debtor based on split_type"""
    split_type = debtor.get("split_type", "equal")
    raw_amount = float(debtor["amount"])
    
    if split_type == "equal":
        # For equal split, each person has amount = 1
        return expense_amount / len(all_debtors)
    
    elif split_type == "percentage":
        # Raw amount is percentage (e.g., 50 for 50%)
        return (expense_amount * raw_amount) / 100
    
    elif split_type == "portion":
        # Raw amount is portions (e.g., 30, 15, 15)
        total_portions = sum(float(d["amount"]) for d in all_debtors)
        if total_portions == 0:
            return 0
        return (expense_amount * raw_amount) / total_portions
    
    else:
        # Fallback for unknown split types
        return raw_amount


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
    
    # Create expense lookup for quick access
    expense_lookup = {e["id"]: e for e in expenses}
    expense_ids = [e["id"] for e in expenses]

    # 4. Aggregate "paid" by payer
    for e in expenses:
        payer_id = e["payer_id"]
        if payer_id in balances:
            balances[payer_id]["paid"] += float(e["amount"])

    # 5. Get debtors only for this group's expenses (with split_type)
    if expense_ids:
        debtors = (
            supabase.table("expenses_debtors")
            .select("person_id, amount, expense_id, split_type")
            .in_("expense_id", expense_ids)
            .execute()
            .data
        )

        # Group debtors by expense_id for proper portion calculation
        debtors_by_expense = {}
        for d in debtors:
            expense_id = d["expense_id"]
            if expense_id not in debtors_by_expense:
                debtors_by_expense[expense_id] = []
            debtors_by_expense[expense_id].append(d)

        # Calculate actual amounts and aggregate "owes"
        for expense_id, expense_debtors in debtors_by_expense.items():
            expense = expense_lookup.get(expense_id)
            if not expense:
                continue
            
            expense_amount = float(expense["amount"])
            
            for debtor in expense_debtors:
                person_id = debtor["person_id"]
                if person_id in balances:
                    calculated_amount = calculate_debtor_amount(
                        debtor, expense_amount, expense_debtors
                    )
                    balances[person_id]["owes"] += calculated_amount

    # 6. Compute net balance
    for person_id, data in balances.items():
        data["balance"] = data["paid"] - data["owes"]

    return balances
