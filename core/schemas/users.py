from typing import Optional, Union
from pydantic import BaseModel


class User(BaseModel):
    """Модель пользователя."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    """Модель пользователя в базе данных."""
    hashed_password: str


class ResponseTemplateOut(BaseModel):
    """Модель ответов."""
    message: str = "success"
    errors: list = []
    payload: dict = {}
