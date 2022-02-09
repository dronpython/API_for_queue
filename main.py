import asyncio
import pathlib
import logging
from typing import Callable, Optional
from uuid import uuid4
import requests

import uvicorn
import json
from fastapi import FastAPI, HTTPException, status, Request, Response, APIRouter
from fastapi.routing import APIRoute

from core.services.security import get_creds
from core.settings import config
from core.connectors.DB import DB, select_done_req_with_response
from core.connectors.LDAP import ldap

logger = logging.getLogger(__name__)

DEFAULT_STATUS = 'pending'
MAIN_TABLE = 'queue_main'
REQUEST_TABLE = 'queue_requests'
ACL_TABLE = 'acl'


class ContextIncludedRoute(APIRoute):
    """
    Класс-роутер, обрабатывающий запросы, требующие добавления информации в базу данных
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            if request.headers.get('authorization'):
                if 'Basic' in request.headers.get('authorization'):
                    credentials_answer = await get_creds(request)
                    logger.info('GOT BASIC AUTH')
                    if not credentials_answer:
                        logger.info('NO CREDENTIALS IN HEADER')
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Can not find auth header',
                        )
                    username, password = credentials_answer
                    logger.info('GOT USERNAME AND PASSWORD')
                else:
                    logger.info('GOT NO AUTH')
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='Token or Basic authorize required',
                    )
                result: bool = ldap._check_auth(server=config.fields.get('servers').get('ldap'), domain='SIGMA',
                                                login=username, password=password)
                if not result:
                    logger.info('USER NOT AUTHORIZED IN LDAP')
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='User not authorized in ldap',
                    )
            elif request.headers.get('token'):
                token: str = request.headers['token']
                token_db: str = DB.select_data('tokens', param_name='token', param_value=token, fetch_one=True)
                if token_db:
                    username = token_db.get('user')
                else:
                    logger.info('NO SUCH TOKEN IN DB')
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='Authorize required',
                    )
            else:
                logger.info('GOT NO AUTH')
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Token or Basic auth required',
                )
            response: Response = await original_route_handler(request)

            request_status: str = DEFAULT_STATUS
            request_id: str = str(uuid4())
            path: str = request.url.path
            method: str = request.method
            if await request.body():
                body = await request.json()
            elif method == 'GET':
                body = dict(request.query_params)
            else:
                body = {}
            body = json.dumps(body)
            headers = json.dumps(dict(request.headers))

            log_info = f'Request_id: {request_id}. '
            # ToDo check domain
            logger.info(f'{log_info} Got request with params: endpoint: {path}, body: {body}, '
                        f'headers: {headers}, username: {username}, status: {request_status}, method: {method}')
            DB.insert_data(MAIN_TABLE, request_id, path, 'sigma', username, request_status)
            DB.insert_data(REQUEST_TABLE, request_id, method, path, body, headers, '')

            acl_data = DB.select_data(ACL_TABLE, 'user', username, fetch_one=True)
            dt: Optional[int] = acl_data.get('dt')
            if dt is None:
                dt = 1
                # dt = int(config.fields.get('default_dt'))
            logger.info(f'{log_info} User dt is: {dt}. Waiting for response..')

            for i in range(dt):
                if DB.universal_select(select_done_req_with_response.format(request_id)):
                    query_result = DB.universal_select(select_done_req_with_response.format(request_id))
                    logger.info(f'Come to result with {query_result}')
                    logger.info(f'{log_info} Got response. Status: {query_result[0].status}. Body: {query_result[0].response_body}')
                    body = {'message': query_result[0].status,
                            'response': query_result[0].response_body,
                            'request_id': request_id}
                    response.body = str(body).encode()
                    response.body = json.dumps(body).encode()
                    response.headers['content-length'] = str(len(response.body))
                    return response
                else:
                    await asyncio.sleep(1)
            logger.info(f'{log_info} Response not found. Return id: {request_id}')
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
    a = request.headers.get('authorization')
    token = requests.post(config.fields.get('api_server') + '/api/v3/svc/get_token', json={}, headers=request.headers)
    print(token)
    return {'token':token}


@app.get('/queue/request/{request_id}')
async def get_request(request_id: str, response: Response):
    """Получить информацию о запросе по request_uuid"""
    result_main: dict = DB.select_data('queue_main', 'status', param_name='request_id',
                                       param_value=request_id, fetch_one=True)
    if result_main:
        response.status_code = status.HTTP_200_OK
        if result_main['status'] == 'done':
            result_responses = DB.select_data('queue_responses', param_name='request_id',
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
