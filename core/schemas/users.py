from typing import Optional, Union
from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str

class ResponseTemplateOut(BaseModel):
    response_status: str = '200 OK'
    message: str = 'default message'
    errors: Union[list, str] = ''
    payload: Union[dict, str] = ''
