from sqlmodel import SQLModel, Field
import time
from typing import Optional

class ChatMessage(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    prompt: str
    response: Optional[str] = Field(default=None)
    created_at: int = Field(default_factory=lambda: int(time.time()))

