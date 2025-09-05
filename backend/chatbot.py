# # main.py
# import anthropic
# import json
# from typing import List, Dict, Any

# client = anthropic.Anthropic(api_key="your-anthropic-key")

# # Tool definitions for Claude (slightly different format)
# TOOLS = [
#     {
#         "name": "add_expense",
#         "description": "Add a new expense to split between users in the expense splitting app",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "amount": {
#                     "type": "number",
#                     "description": "The amount of money spent",
#                 },
#                 "currency": {
#                     "type": "string",
#                     "description": "Currency code like EUR, USD, GBP",
#                     "default": "EUR",
#                 },
#                 "payer": {
#                     "type": "string",
#                     "description": "Name of person who paid for the expense",
#                 },
#                 "description": {
#                     "type": "string",
#                     "description": "Description of what the expense was for (e.g., 'groceries', 'dinner', 'taxi')",
#                 },
#                 "participants": {
#                     "type": "array",
#                     "items": {"type": "string"},
#                     "description": "List of people to split the expense with. If not specified, assume all group members.",
#                 },
#                 "group_id": {
#                     "type": "string",
#                     "description": "ID of the group this expense belongs to",
#                 },
#             },
#             "required": ["amount", "payer", "description"],
#         },
#     },
#     {
#         "name": "get_expenses",
#         "description": "Retrieve expenses for a user or group",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "group_id": {
#                     "type": "string",
#                     "description": "ID of the group to get expenses for",
#                 },
#                 "user_id": {
#                     "type": "string",
#                     "description": "ID of specific user to filter by",
#                 },
#                 "limit": {
#                     "type": "integer",
#                     "description": "Number of recent expenses to return",
#                     "default": 10,
#                 },
#             },
#         },
#     },
# ]


# @app.post("/chat")
# async def chat_with_claude(request: ChatRequest):
#     try:
#         # Build message history
#         messages = [{"role": "user", "content": request.message}]

#         # Initial call to Claude
#         response = client.messages.create(
#             model="claude-3-5-sonnet-20241022",  # or claude-3-opus-20240229
#             max_tokens=1000,
#             messages=messages,
#             tools=TOOLS,
#             system=f"""You are a helpful assistant for an expense splitting app.
#             Current user ID: {request.user_id}
#             Current group ID: {request.group_id}

#             When users want to add expenses, extract the details and use the add_expense tool.
#             When they ask about expenses or balances, use the get_expenses tool.

#             Be conversational and friendly. If information is missing, make reasonable assumptions or ask for clarification.""",
#         )

#         # Check if Claude wants to use tools
#         if response.stop_reason == "tool_use":
#             # Execute the tools
#             tool_results = []

#             for content_block in response.content:
#                 if content_block.type == "tool_use":
#                     tool_name = content_block.name
#                     tool_input = content_block.input
#                     tool_use_id = content_block.id

#                     # Execute the appropriate function
#                     if tool_name == "add_expense":
#                         result = await execute_add_expense(
#                             tool_input, request.user_id, request.group_id
#                         )
#                         tool_results.append(
#                             {
#                                 "tool_use_id": tool_use_id,
#                                 "type": "tool_result",
#                                 "content": json.dumps(result),
#                             }
#                         )

#                     elif tool_name == "get_expenses":
#                         result = await execute_get_expenses(tool_input)
#                         tool_results.append(
#                             {
#                                 "tool_use_id": tool_use_id,
#                                 "type": "tool_result",
#                                 "content": json.dumps(result),
#                             }
#                         )

#             # Send tool results back to Claude for final response
#             messages.append({"role": "assistant", "content": response.content})
#             messages.append({"role": "user", "content": tool_results})

#             final_response = client.messages.create(
#                 model="claude-3-5-sonnet-20241022",
#                 max_tokens=1000,
#                 messages=messages,
#                 tools=TOOLS,
#             )

#             # Extract text content from response
#             text_content = ""
#             for content in final_response.content:
#                 if content.type == "text":
#                     text_content += content.text

#             return {"response": text_content}

#         else:
#             # Regular text response
#             text_content = ""
#             for content in response.content:
#                 if content.type == "text":
#                     text_content += content.text
#             return {"response": text_content}

#     except Exception as e:
#         return {"error": str(e)}


# # Tool execution functions
# async def execute_add_expense(
#     tool_input: Dict[str, Any], user_id: str, group_id: str
# ) -> Dict:
#     try:
#         # Add user context
#         expense_data = ExpenseFunction(
#             **tool_input, group_id=group_id or tool_input.get("group_id")
#         )

#         # Your existing database logic
#         result = await add_expense_to_db(expense_data, user_id)

#         return {
#             "success": True,
#             "expense": result,
#             "message": f"Added expense of {expense_data.amount} {expense_data.currency} for {expense_data.description}",
#         }
#     except Exception as e:
#         return {"success": False, "error": str(e)}


# async def execute_get_expenses(tool_input: Dict[str, Any]) -> Dict:
#     try:
#         # Your existing logic to fetch expenses
#         expenses = await get_expenses_from_db(
#             group_id=tool_input.get("group_id"),
#             user_id=tool_input.get("user_id"),
#             limit=tool_input.get("limit", 10),
#         )

#         return {"success": True, "expenses": expenses, "count": len(expenses)}
#     except Exception as e:
#         return {"success": False, "error": str(e)}


# class ChatRequest(BaseModel):
#     message: str
#     user_id: str
#     group_id: Optional[str] = None
