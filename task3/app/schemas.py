from typing import Optional
from pydantic import BaseModel


class Message(BaseModel):
    type: str
    text: Optional[str] = None
    room_id: Optional[str] = None
    username: Optional[str] = None
    detail: Optional[str] = None


class ErrorMessage(BaseModel):
    type: str
    detail: str


class UserListResponse(BaseModel):
    room_id: str
    users: list