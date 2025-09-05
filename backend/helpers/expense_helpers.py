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
    print(response)
    return response.data[0]


async def create_debtors_records(
    supabase, expense_id: str, expense_amount: float, debtors: list
):
    """Create debtor records for expense"""
    share_amount = expense_amount / len(debtors)
    debtors_data = [
        {"expense_id": expense_id, "person_id": debtor_id, "amount": share_amount}
        for debtor_id in debtors
    ]
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
    print(expense_data)
    return (
        supabase.table("expenses")
        .update(expense_data.model_dump(exclude_unset=True))
        .eq("id", expense_id)
        .execute()
    )
