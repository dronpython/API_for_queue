import logging
from typing import Optional

from fastapi import Request

from core.connectors.DB import DB
from core.services.data_processing import get_data_from_request, is_hashed_data_exist
from core.settings import config

DEFAULT_STATUS = 'pending'
MAIN_TABLE = 'queue_main'
REQUEST_TABLE = 'queue_requests'
ACL_TABLE = 'acl'
HASHED_DATA_TABLE = 'queue_hashed'
RESPONSE_TABLE = 'queue_responses'
PENDING_STATUS = 'pending'
WORKING_STATUS = 'working'

SELECT_DONE_REQ_WITH_RESPONSE: str = """SELECT qm.request_id, qm.status, qr.response_body FROM queue_main qm
JOIN queue_responses qr on qm.request_id = qr.request_id
WHERE qm.request_id = \'{}\' AND (qm.status = 'done' OR qm.status = 'error')"""

logger = logging.getLogger(__name__)


async def is_data_added_to_db(request: Request, username: str, request_id: str, hashed_data: str) -> bool:
    """Проверяет добавлена ли запись о запросе в базу, если нет - значит он уже есть в базе.
    """
    request_status: str = DEFAULT_STATUS
    path, method, body, headers = await get_data_from_request(request)
    log_info = f'Request_id: {request_id}. '
    # ToDo check domain
    logger.info(f'{log_info} Got request with params: endpoint: {path}, body: {body}, '
                f'headers: {headers}, username: {username}, status: {request_status}, method: {method}')
    if not await is_hashed_data_exist(hashed_data):
        DB.insert_data(MAIN_TABLE, request_id, path, 'sigma', username, request_status)
        DB.insert_data(REQUEST_TABLE, request_id, method, path, body, headers, '')
        DB.insert_data(HASHED_DATA_TABLE, request_id, hashed_data)
        return True
    return False


async def get_dt(username: str, request_id: str) -> int:
    """Получить время ожидания для пользователя.
    """
    acl_data: dict = DB.select_data(ACL_TABLE, 'user', username, fetch_one=True)
    delta_time: Optional[int] = acl_data.get('dt')
    if delta_time is None:
        delta_time = int(config.fields.get('default_dt'))
    logger.info(f'Request id: {request_id}. User dt is: {delta_time}. Waiting for response..')
    return delta_time


async def get_hashed_data_from_db(hashed_data: str) -> dict:
    """Получить запрос с определенным хэшем.
    """
    same_data: dict = DB.select_data(HASHED_DATA_TABLE, param_name='hash_data', param_value=hashed_data, fetch_one=True)
    return same_data


async def is_request_done(request_id: str) -> bool:
    """Проверить выполнен ли запрос.
    """
    if DB.universal_select(SELECT_DONE_REQ_WITH_RESPONSE.format(request_id)):
        return True
    return False


async def get_status(request_id: str) -> str:
    """Получить статус запроса по request_id.
    """
    field_name: str = 'request_id'
    result_main: dict = DB.select_data(MAIN_TABLE, param_name=field_name,
                                       param_value=request_id, fetch_one=True)
    request_status: str = result_main['status']
    return request_status
