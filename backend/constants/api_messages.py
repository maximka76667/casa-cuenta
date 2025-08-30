# API response messages constants


# Success messages
class SuccessMessages:
    # Expenses
    EXPENSE_ADDED = "Expense added successfully"
    EXPENSE_UPDATED = "Expense updated successfully"
    EXPENSE_DELETED = "Expense deleted successfully"

    # Groups
    GROUP_ADDED = "Group added successfully"
    GROUP_UPDATED = "Group updated successfully"
    GROUP_DELETED = "Group deleted successfully"

    # Persons
    PERSON_ADDED = "Person added successfully"
    PERSON_UPDATED = "Person updated successfully"
    PERSON_DELETED = "Person deleted successfully"

    # Debtors
    DEBTOR_ADDED = "Debtor added successfully"
    DEBTOR_UPDATED = "Debtor updated successfully"
    DEBTOR_DELETED = "Debtor deleted successfully"

    # Members
    MEMBER_ADDED = "Member added successfully"
    MEMBER_UPDATED = "Member updated successfully"
    MEMBER_DELETED = "Member deleted successfully"


# Error messages
class ErrorMessages:
    # General errors
    INVALID_TOKEN = "Invalid token"
    UNAUTHORIZED = "Unauthorized access"
    NOT_FOUND = "Resource not found"
    VALIDATION_ERROR = "Validation error"

    # Database errors
    EXPENSE_NOT_FOUND = "Expense not found"
    GROUP_NOT_FOUND = "Group not found"
    PERSON_NOT_FOUND = "Person not found"
    DEBTOR_NOT_FOUND = "Debtor not found"
    MEMBER_NOT_FOUND = "Member not found"
    USER_NOT_FOUND = "User not found"

    # Operation errors
    ERROR_ADDING_PERSON = "Error on adding person"
    ERROR_DELETING_PERSON = "Error on deleting person"
    ERROR_UPDATING_PERSON = "Error on updating person"
    ERROR_ADDING_EXPENSE = "Error on adding expense"
    ERROR_DELETING_EXPENSE = "Error on deleting expense"
    ERROR_UPDATING_EXPENSE = "Error on updating expense"
    ERROR_ADDING_GROUP = "Error creating group"
    ERROR_DELETING_GROUP = "Error deleting group"
    ERROR_UPDATING_GROUP = "Error updating group"
    ERROR_ADDING_DEBTOR = "Error creating debtor"
    ERROR_DELETING_DEBTOR = "Error deleting debtor"
    ERROR_UPDATING_DEBTOR = "Error updating debtor"
    ERROR_ADDING_MEMBER = "Error creating member"
    ERROR_DELETING_MEMBER = "Error deleting member"
    ERROR_UPDATING_MEMBER = "Error updating member"
    ERROR_RETRIEVING_USER_GROUPS = "Error retrieving user groups"

    # Business logic errors
    INSUFFICIENT_PERMISSIONS = "Insufficient permissions for this operation"
    CANNOT_DELETE_GROUP_WITH_EXPENSES = "Cannot delete group that has expenses"
    INVALID_EXPENSE_AMOUNT = "Expense amount must be greater than zero"
    INVALID_DEBTOR_SPLIT = "Debtor amounts must sum to total expense amount"


# Info messages
class InfoMessages:
    # Cache messages
    CACHE_HIT = "Data retrieved from cache"
    CACHE_MISS = "Data retrieved from database"
    CACHE_INVALIDATED = "Cache invalidated successfully"

    # Process messages
    PROCESSING_REQUEST = "Processing request..."
    CALCULATING_BALANCES = "Calculating group balances..."
    VALIDATING_DATA = "Validating input data..."


# HTTP status messages (for consistency)
class StatusMessages:
    OK = "Request successful"
    CREATED = "Resource created successfully"
    UPDATED = "Resource updated successfully"
    DELETED = "Resource deleted successfully"
    BAD_REQUEST = "Bad request - invalid input"
    UNAUTHORIZED = "Authentication required"
    FORBIDDEN = "Access forbidden"
    NOT_FOUND = "Resource not found"
    INTERNAL_ERROR = "Internal server error"


# Response builders (optional utility functions)
def success_response(message: str, data=None):
    """Build a standardized success response"""
    response = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return response


def error_response(message: str, error_code: str = None, details=None):
    """Build a standardized error response"""
    response = {"success": False, "message": message}
    if error_code:
        response["error_code"] = error_code
    if details:
        response["details"] = details
    return response


# Entity-specific message functions (for consistency)
class EntityMessages:
    @staticmethod
    def entity_added(entity_name: str) -> str:
        return f"{entity_name.capitalize()} added successfully"

    @staticmethod
    def entity_updated(entity_name: str) -> str:
        return f"{entity_name.capitalize()} updated successfully"

    @staticmethod
    def entity_deleted(entity_name: str) -> str:
        return f"{entity_name.capitalize()} deleted successfully"

    @staticmethod
    def entity_not_found(entity_name: str) -> str:
        return f"{entity_name.capitalize()} not found"
