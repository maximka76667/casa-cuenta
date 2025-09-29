from models.expense import ExpenseCreate


async def get_all_expenses_from_db(supabase):
    """Get all expenses from database"""
    return supabase.table("expenses").select("*").execute().data


async def get_group_expenses_from_db(supabase, group_id: str):
    """Get expenses for specific group from database"""
    return (
        supabase.table("expenses").select("*").eq("group_id", group_id).execute().data
    )


async def create_expense_record(supabase, expense: ExpenseCreate):
    """Create expense record in database"""
    new_expense = {
        "name": expense.name,
        "amount": expense.amount,
        "payer_id": expense.payer_id,
        "group_id": expense.group_id,
    }
    response = supabase.table("expenses").insert(new_expense).execute()
    return response.data[0]


async def create_debtors_records(
    supabase, expense_id: str, expense_amount: float, debtors: list, split_type: str
):
    """Create debtor records for an expense"""
    """Store raw values (portions/percentages) not calculated dollar amounts"""

    # Check if debtors are strings (equal split) or dicts/objects (percentage/portion)
    is_simple_list = isinstance(debtors[0], str)

    if split_type == "equal":
        # For equal split, store equal portion for each debtor (e.g., 1 portion each)
        debtors_data = [
            {
                "expense_id": expense_id,
                "person_id": (
                    debtor
                    if is_simple_list
                    else (debtor.get("id") if isinstance(debtor, dict) else debtor.id)
                ),
                "amount": 1,  # Store raw portion value
                "split_type": "equal",
            }
            for debtor in debtors
        ]

    elif split_type == "portion":
        # Store the raw portion values (e.g., 30, 15, 15)
        debtors_data = [
            {
                "expense_id": expense_id,
                "person_id": (
                    debtor.get("id") if isinstance(debtor, dict) else debtor.id
                ),
                "amount": (
                    debtor.get("value", 1) if isinstance(debtor, dict) else debtor.value
                ),
                "split_type": "portion",
            }
            for debtor in debtors
        ]

    elif split_type == "percentage":
        # Store the raw percentage values (e.g., 50, 30, 20)
        debtors_data = [
            {
                "expense_id": expense_id,
                "person_id": (
                    debtor.get("id") if isinstance(debtor, dict) else debtor.id
                ),
                "amount": (
                    debtor.get("value", 0) if isinstance(debtor, dict) else debtor.value
                ),
                "split_type": "percentage",
            }
            for debtor in debtors
        ]

    else:
        raise ValueError("Invalid split_type")

    response = supabase.table("expenses_debtors").insert(debtors_data).execute()
    return response.data


async def get_expense_group_id(supabase, expense_id: str):
    """Get group_id for specific expense"""
    response = (
        supabase.table("expenses").select("group_id").eq("id", expense_id).execute()
    )
    return response.data[0]["group_id"] if response.data else None


async def delete_expense_from_db(supabase, expense_id: str):
    """Delete expense from database"""
    return supabase.table("expenses").delete().eq("id", expense_id).execute()


async def update_expense_in_db(supabase, expense_id: str, expense_data):
    """Update expense in database"""
    return (
        supabase.table("expenses")
        .update(expense_data.model_dump(exclude_unset=True))
        .eq("id", expense_id)
        .execute()
    )
