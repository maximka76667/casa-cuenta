from models.expense_debtor import ExpenseDebtorIn, ExpenseDebtorUpdate


async def get_all_debtors_from_db(supabase):
    """Get all debtors from database"""
    return supabase.table("expenses_debtors").select("*").execute().data


async def get_group_debtors_from_db(supabase, group_id: str):
    """Get debtors for specific group from database"""
    return (
        supabase.from_("expenses_debtors")
        .select("*, expenses(group_id)")
        .eq("expenses.group_id", group_id)
        .execute()
        .data
    )


async def create_debtor_record(supabase, debtor: ExpenseDebtorIn):
    """Create debtor record in database"""
    response = supabase.table("expenses_debtors").insert(debtor.model_dump()).execute()
    return response.data[0] if response.data else None


async def get_debtor_expense_id(supabase, debtor_id: str):
    """Get expense_id for specific debtor"""
    response = (
        supabase.table("expenses_debtors")
        .select("expense_id")
        .eq("id", debtor_id)
        .execute()
    )
    return response.data[0]["expense_id"] if response.data else None


async def get_expense_group_id_from_expense(supabase, expense_id: str):
    """Get group_id from expense_id"""
    if not expense_id:
        return None
    response = (
        supabase.table("expenses").select("group_id").eq("id", expense_id).execute()
    )
    return response.data[0]["group_id"] if response.data else None


async def delete_debtor_from_db(supabase, debtor_id: str):
    """Delete debtor from database"""
    response = supabase.table("expenses_debtors").delete().eq("id", debtor_id).execute()
    return response.data


async def update_debtor_in_db(supabase, debtor_id: str, debtor: ExpenseDebtorUpdate):
    """Update debtor in database"""
    response = (
        supabase.table("expenses_debtors")
        .update(debtor.model_dump())
        .eq("id", debtor_id)
        .execute()
    )
    return response.data

