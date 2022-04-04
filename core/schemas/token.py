from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Модель токена."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Модель данных у токена."""
    username: Optional[str] = None
