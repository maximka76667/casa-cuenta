from typing import Any, Dict, List
from pydantic import BaseModel


class UserGroupsResponse(BaseModel):
    groups: List[Dict[str, Any]]
