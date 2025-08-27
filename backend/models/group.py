from pydantic import BaseModel

class GroupIn(BaseModel):
    name: str

class GroupUpdate(BaseModel):
    name: str | None = None
