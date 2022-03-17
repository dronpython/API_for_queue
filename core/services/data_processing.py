import json
from typing import Optional, Tuple
from fastapi import Request

from core.services import database_utility as db_util


async def is_hashed_data_exist(hashed_data: str) -> bool:
    """Есть ли в базе запись с таким же хэшем.
    """
    hashed_data_in_db: Optional[dict] = await db_util.get_hashed_data_from_db(hashed_data)
    if hashed_data_in_db:
        return True
    return False


async def handle_body(method: str, request: Request) -> str:
    """Обработка тела запроса при разных ситуациях.
    """
    if await request.body():
        body = await request.json()
    elif method == 'GET':
        body = dict(request.query_params)
    else:
        body = {}
    body = json.dumps(body)
    return body


async def get_data_from_request(request: Request) -> Tuple:
    """Получить данные из запроса
    """
    path: str = request.url.path
    method: str = request.method
    body = await handle_body(method, request)
    headers = json.dumps(dict(request.headers))
    return path, method, body, headers
