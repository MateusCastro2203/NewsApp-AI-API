from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    user_id: str
    message: str
    url: Optional[str] = None
    conversation_id: Optional[str] = None