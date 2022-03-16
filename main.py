import asyncio
import pathlib
import logging
from typing import Callable, Optional
from uuid import uuid4

import uvicorn
import json
from fastapi import FastAPI, status, Request, Response, APIRouter
from fastapi.routing import APIRoute

from core.services.security import get_token, verify_request, get_hash
from core.settings import config
from core.connectors.DB import DB
from core.services.database_utility import is_data_added_to_db, is_request_done, get_dt, get_status, \
    get_hashed_data_from_db, MAIN_TABLE, RESPONSE_TABLE, SELECT_DONE_REQ_WITH_RESPONSE, PENDING_STATUS, WORKING_STATUS
from core.services.data_processing import get_data_from_request

logger = logging.getLogger(__name__)


class ContextIncludedRoute(APIRoute):
    """
    Класс-роутер, обрабатывающий запросы, требующие добавления информации в базу данных
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            username = await verify_request(request.headers)
            request_id: str = str(uuid4())

            response: Response = await original_route_handler(request)

            _, _, body, headers = await get_data_from_request(request)
            data_for_hash: str = f"{str(headers)}:{str(body)}"
            hashed_data = await get_hash(data_for_hash)

            data_added = await is_data_added_to_db(request, username, request_id, hashed_data)

            if not data_added:
                hashed_data_from_db = await get_hashed_data_from_db(hashed_data)
                hashed_data_request_id = hashed_data_from_db['request_id']
                hashed_data_status = await get_status(hashed_data_request_id)
                if hashed_data_status.lower() in [PENDING_STATUS, WORKING_STATUS]:
                    body = {'message': 'same request already in progress',
                            'request_id': hashed_data_request_id
                            }
                    response.body = json.dumps(body).encode()
                    response.headers['content-length'] = str(len(response.body))
                    return response

            delta_time = await get_dt(username, request_id)

            for _ in range(delta_time):
                if is_request_done(request_id):
                    query_result = DB.universal_select(SELECT_DONE_REQ_WITH_RESPONSE.format(request_id))
                    logger.info(f'Come to result with {query_result}')
                    logger.info(f'Request_id: {request_id} Got response. Status: {query_result[0].status}. '
                                f'Body: {query_result[0].response_body}')
                    body = {'message': query_result[0].status,
                            'response': query_result[0].response_body,
                            'request_id': request_id}
                    response.body = str(body).encode()
                    response.body = json.dumps(body).encode()
                    response.headers['content-length'] = str(len(response.body))
                    return response
                await asyncio.sleep(1)

            logger.info(f'Request_id: {request_id} Response not found. Return id: {request_id}')
            body = {'message': 'success', 'request_id': request_id}

            response.body = str(body).encode()
            response.body = json.dumps(body).encode()
            response.headers['content-length'] = str(len(response.body))
            return response

        return custom_route_handler


app = FastAPI()
router = APIRouter(route_class=ContextIncludedRoute)


@app.post('/api/v3/svc/get_token')
async def login_for_access_token_new(request: Request):
    """Получить токен новый
    """
    token = await get_token(request.headers)
    return {'token': token}


@app.get('/queue/request/{request_id}')
async def get_request(request_id: str, response: Response):
    """Получить информацию о запросе по request_uuid"""
    result_main: dict = DB.select_data(MAIN_TABLE, 'status', param_name='request_id',
                                       param_value=request_id, fetch_one=True)
    if result_main:
        response.status_code = status.HTTP_200_OK
        if result_main['status'] == 'done':
            result_responses = DB.select_data(RESPONSE_TABLE, param_name='request_id',
                                              param_value=request_id, fetch_one=True)
            payload = {
                'request_id': result_responses['request_id'],
                'endpoint': result_main['endpoint'],
                'status': result_main['status'],
                'body': result_responses['response_body']
            }
        else:
            payload = {
                'request_id': result_main['request_id'],
                'endpoint': result_main['endpoint'],
                'status': result_main['status'],
                'body': {}
            }
        return payload
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "not found such request id"}


@app.put('/queue/request/{request_id}')
async def update_request(request_id: str, request: Request):
    """Обновить информацию о запросе по request_id"""
    body: dict = await request.json()
    param_name = 'request_id'
    result: dict = DB.update_data(MAIN_TABLE, field_name=body['field'], field_value=body['value'],
                                  param_name=param_name,
                                  param_value=request_id)
    return result


@app.get('/queue/info')
async def get_queue_info(status: Optional[str] = None, period: Optional[int] = None, endpoint: Optional[str] = None,
                         directory: Optional[str] = None):
    """Получить информацию об очереди"""
    result: dict = DB.get_queue_statistics(status=status, period=period, endpoint=endpoint, directory=directory)
    return result


@app.get('/queue/processing_info')
async def get_queue_info(status: Optional[str] = None, period: Optional[str] = None, endpoint: Optional[str] = None,
                         directory: Optional[str] = None):
    """Получить информацию об очереди"""
    pass


@app.get('/queue/get_requests_status')
async def get_queue_info(status: Optional[str]):
    """Получить информацию об очереди"""
    result: dict = DB.get_queue_statistics(status=status)
    return result


@router.api_route("/{path_name:path}", methods=["GET", "POST"])
async def catch_all():
    """Метод перехватывающий любой запрос, кроме объявленных выше"""
    return 1


app.include_router(router)

if __name__ == '__main__':
    parent_directory = pathlib.Path(__file__).parent.resolve()
    config_file = str(parent_directory) + config.fields.get('path').get('config')
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True, log_config=config_file)
