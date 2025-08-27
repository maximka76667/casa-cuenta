from pydantic import BaseModel

class GroupUserIn(BaseModel):
    group_id: str
    user_id: str

class GroupUserUpdate(BaseModel):
    group_id: str | None = None
    user_id: str | None = None