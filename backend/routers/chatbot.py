import anthropic
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from difflib import SequenceMatcher

# Dependencies and helpers
from dependencies import get_redis, get_supabase
from helpers.expense_helpers import (
    get_all_expenses_from_db,
    get_group_expenses_from_db,
    create_expense_record,
    create_debtors_records,
)
from helpers.group_helpers import get_group_persons_from_db
from models.expense import ExpenseCreate

# Middlewares
from middlewares.rate_limiter import basic_rate_limit, strict_rate_limit
from middlewares.logger import get_logger, log_cache_operation

# Cache
from helpers.cache_helpers import (
    get_cached_items,
    cache_items,
    invalidate_cache,
    remove_item_from_cache,
    update_item_cache,
)
from constants.cache_keys import (
    EXPENSES_ALL,
    group_balances_cache_key,
    group_debtors_cache_key,
    group_expenses_cache_key,
)

import os

from utils import dump_json

router = APIRouter(
    prefix="/chat",
    tags=["chatbot"],
)

logger = get_logger()

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Tool definitions for Claude
TOOLS = [
    {
        "name": "add_expense",
        "description": "Add a new expense to split between users in the expense splitting app",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "The amount of money spent",
                },
                "payer": {
                    "type": "string",
                    "description": "Name of person who paid for the expense",
                },
                "name": {
                    "type": "string",
                    "description": "Description of what the expense was for (e.g., 'groceries', 'dinner', 'taxi')",
                },
                "debtors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of persond ids to split the expense with. If not specified, assume all group members.",
                },
            },
            "required": ["amount", "payer", "name"],
        },
    },
    {
        "name": "get_expenses",
        "description": "Retrieve expenses for a group",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of recent expenses to return",
                    "default": 10,
                },
            },
        },
    },
]


class ChatRequest(BaseModel):
    message: str
    group_id: str


@router.post("/")
@strict_rate_limit()
async def chat_with_claude(
    request: Request,
    request_data: ChatRequest,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    supabase=Depends(get_supabase),
):
    """Chat with Claude AI assistant for expense management"""
    try:
        logger.info(f"Chat request in group {request_data.group_id}")

        # Build message history
        messages = [{"role": "user", "content": request_data.message}]

        # Initial call to Claude
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            messages=messages,
            tools=TOOLS,
            system=f"""You are a helpful assistant for an expense splitting app.
            Current group ID: {request_data.group_id}

            When users want to add expenses, extract the details and use the add_expense tool.
            When they ask about expenses or balances, use the get_expenses tool.

            Be conversational and friendly. If information is missing, make reasonable assumptions or ask for clarification.""",
        )

        # Check if Claude wants to use tools
        if response.stop_reason == "tool_use":
            # Execute the tools
            tool_results = []

            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    tool_use_id = content_block.id

                    logger.info(f"Executing tool: {tool_name} with input: {tool_input}")

                    # Execute the appropriate function
                    if tool_name == "add_expense":
                        result = await execute_add_expense(
                            tool_input,
                            request_data.group_id,
                            background_tasks,
                            redis_client,
                            supabase,
                        )
                        tool_results.append(
                            {
                                "tool_use_id": tool_use_id,
                                "type": "tool_result",
                                "content": dump_json(result),
                            }
                        )

                    elif tool_name == "get_expenses":
                        result = await execute_get_expenses(
                            tool_input,
                            request_data.group_id,
                            redis_client,
                            supabase,
                            background_tasks,
                        )
                        tool_results.append(
                            {
                                "tool_use_id": tool_use_id,
                                "type": "tool_result",
                                "content": dump_json(result),
                            }
                        )

            # Send tool results back to Claude for final response
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            final_response = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                messages=messages,
                tools=TOOLS,
                system=f"If you added expense i need you always to start message with 'Successfully added'",
            )

            # Extract text content from response
            text_content = ""
            for content in final_response.content:
                if content.type == "text":
                    text_content += content.text

            logger.info(f"Chat completed successfully")
            return {"response": text_content}

        else:
            # Regular text response
            text_content = ""
            for content in response.content:
                if content.type == "text":
                    text_content += content.text

            logger.info(f"Chat completed with text response")
            return {"response": text_content}

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")


def find_person_by_name(input_name: str, persons: List[dict]) -> tuple:
    """
    Smart name matching that handles partial names, first/last names, and fuzzy matching
    Returns: (person_id, confidence, matched_name) or (None, 0, None)
    """
    input_name = input_name.lower().strip()

    # Exact matches (highest priority)
    for person in persons:
        if person["name"].lower() == input_name:
            return person["id"], 1.0, person["name"]

    # First name or last name exact matches
    for person in persons:
        name_parts = person["name"].lower().split()
        if input_name in name_parts:
            return person["id"], 0.9, person["name"]

    # Partial matches (starts with)
    for person in persons:
        name_parts = person["name"].lower().split()
        for part in name_parts:
            if part.startswith(input_name) and len(input_name) >= 2:
                return person["id"], 0.8, person["name"]

    # Fuzzy matching (for typos)
    best_match = None
    best_score = 0.6  # Minimum confidence threshold

    for person in persons:
        # Check against full name
        full_name_score = SequenceMatcher(
            None, input_name, person["name"].lower()
        ).ratio()
        if full_name_score > best_score:
            best_match = (person["id"], full_name_score, person["name"])
            best_score = full_name_score

        # Check against individual name parts
        for part in person["name"].lower().split():
            part_score = SequenceMatcher(None, input_name, part).ratio()
            if part_score > best_score:
                best_match = (person["id"], part_score, person["name"])
                best_score = part_score

    return best_match if best_match else (None, 0, None)


def find_multiple_persons_by_names(
    input_names: List[str], persons: List[dict]
) -> tuple:
    """
    Find multiple persons with smart matching and ambiguity handling
    Returns: (person_ids, errors)
    """
    person_ids = []
    errors = []

    for input_name in input_names:
        person_id, confidence, matched_name = find_person_by_name(input_name, persons)

        if person_id:
            person_ids.append(person_id)
            if confidence < 0.9:  # Log uncertain matches
                logger.info(
                    f"Fuzzy matched '{input_name}' to '{matched_name}' (confidence: {confidence:.2f})"
                )
        else:
            # Try to suggest similar names
            suggestions = []
            for person in persons:
                for part in person["name"].lower().split():
                    if SequenceMatcher(None, input_name.lower(), part).ratio() > 0.5:
                        suggestions.append(person["name"])
                        break

            error_msg = f"'{input_name}' not found in group"
            if suggestions:
                error_msg += f". Did you mean: {', '.join(suggestions[:3])}?"
            errors.append(error_msg)

    return person_ids, errors


# Tool execution functions
async def execute_add_expense(
    tool_input: Dict[str, Any],
    group_id: str,
    background_tasks: BackgroundTasks,
    redis_client,
    supabase,
) -> Dict:
    """Execute the add_expense tool"""
    try:
        # Get group persons to map names to IDs
        persons = await get_group_persons_from_db(supabase, group_id)
        if not persons:
            return {"success": False, "error": "No persons found in group"}

        payer_id, confidence, matched_name = find_person_by_name(
            tool_input["payer"], persons
        )

        if not payer_id:
            # Suggest similar names
            suggestions = []
            for person in persons:
                for part in person["name"].lower().split():
                    if (
                        SequenceMatcher(None, tool_input["payer"].lower(), part).ratio()
                        > 0.5
                    ):
                        suggestions.append(person["name"])
                        break

            error_msg = f"Payer '{tool_input['payer']}' not found in current group"
            if suggestions:
                error_msg += (
                    f". Available people: {', '.join([p['name'] for p in persons])}"
                )
            return {"success": False, "error": error_msg}

        # Log if we made a fuzzy match for the payer
        if confidence < 1.0:
            logger.info(
                f"Matched payer '{tool_input['payer']}' to '{matched_name}' (confidence: {confidence:.2f})"
            )

        # Handle participants - if not specified, use all group members
        debtors = tool_input.get("debtors", [])
        if not debtors:
            debtor_ids = [person["id"] for person in persons]
            logger.info("No debtors specified, using all group members")
        else:
            debtor_ids, errors = find_multiple_persons_by_names(debtors, persons)
            if errors:
                return {
                    "success": False,
                    "error": f"Debtor errors: {'; '.join(errors)}. Available people: {', '.join([p['name'] for p in persons])}",
                }

        # Create expense data
        expense_data = ExpenseCreate(
            name=tool_input["name"],
            amount=float(tool_input["amount"]),
            payer_id=payer_id,
            group_id=group_id,
            debtors=debtor_ids,
        )

        # Create expense record
        expense_result = await create_expense_record(supabase, expense_data)
        if not expense_result:
            return {"success": False, "error": "Failed to create expense"}

        # Create debtors records
        debtors_result = await create_debtors_records(
            supabase, expense_result["id"], expense_data.amount, debtor_ids
        )

        # Invalidate cache in multiple locations
        global_cache_key = EXPENSES_ALL
        group_cache_key = group_expenses_cache_key(group_id)
        balances_cache_key = group_balances_cache_key(group_id)
        debtors_cache_key = group_debtors_cache_key(group_id)

        invalidate_cache(background_tasks, redis_client, global_cache_key)
        invalidate_cache(background_tasks, redis_client, group_cache_key)
        invalidate_cache(background_tasks, redis_client, balances_cache_key)
        invalidate_cache(background_tasks, redis_client, debtors_cache_key)

        log_cache_operation("update", global_cache_key)
        log_cache_operation("update", group_cache_key)
        log_cache_operation("update", balances_cache_key)
        log_cache_operation("update", debtors_cache_key)

        remove_item_from_cache(
            background_tasks, redis_client, group_cache_key, expense_result["id"]
        )

        log_cache_operation("remove", group_cache_key)

        logger.info(
            f"Expense added via chat | ID: {expense_result['id']} | Amount: {expense_data.amount}"
        )

        return {
            "success": True,
            "expense": expense_result,
            "debtors": debtors_result,
            "message": f"Added expense of {expense_data.amount} for {expense_data.name}",
        }
    except Exception as e:
        logger.error(f"Error executing add_expense tool: {str(e)}")
        return {"success": False, "error": str(e)}


async def execute_get_expenses(
    tool_input: Dict[str, Any], group_id: str, redis_client, supabase, background_tasks
) -> Dict:
    """Execute the get_expenses tool"""
    try:
        limit = tool_input.get("limit", 10)

        if group_id:
            # Get group expenses
            cache_key = group_expenses_cache_key(group_id)
            expenses = await get_cached_items(redis_client, cache_key)

            if not expenses:
                expenses = await get_group_expenses_from_db(supabase, group_id)
                cache_items(background_tasks, redis_client, cache_key, expenses)
        else:
            # Get all expenses
            cache_key = EXPENSES_ALL
            expenses = await get_cached_items(redis_client, cache_key)

            if not expenses:
                expenses = await get_all_expenses_from_db(supabase)
                cache_items(background_tasks, redis_client, cache_key, expenses)

        # Apply limit
        if limit and len(expenses) > limit:
            expenses = expenses[:limit]

        logger.info(f"Retrieved {len(expenses)} expenses via chat | Group: {group_id}")

        return {"success": True, "expenses": expenses, "count": len(expenses)}
    except Exception as e:
        logger.error(f"Error executing get_expenses tool: {str(e)}")
        return {"success": False, "error": str(e)}
