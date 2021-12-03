import pathlib
import logging
from typing import Callable, Optional
from uuid import uuid4

import uvicorn
import json
from fastapi import FastAPI, HTTPException, status, Request, Response, APIRouter
from fastapi.routing import APIRoute

from core.services.security import decrypt_password, encrypt_password, InvalidToken, get_creds, old_api_token
from core.settings import config, settings
from core.connectors.DB import DB, select_done_req_with_response
from core.connectors.LDAP import ldap
from core.schemas.users import ResponseTemplateOut

logger = logging.getLogger()


class ContextIncludedRoute(APIRoute):
    """
    Класс-роутер, обрабатывающий запросы, требующие добавления информации в базу данных
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            auth_header: str = request.headers.get('authorization')
            if auth_header:
                headers_dict = dict(request.headers)
                if 'Bearer' in auth_header:
                    try:
                        token: str = auth_header.replace('Bearer ', '')
                        data: str = await decrypt_password(token)
                        logger.info('GOT BEARER TOKEN')
                    except InvalidToken:
                        logger.info('INVALID TOKEN')
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid token',
                        )
                    username, password, date = data.split('|')
                    logger.info('GOT USERNAME, PASSWORD AND EXPIRE DATE')
                elif 'Basic' in auth_header:
                    credentials_answer = await get_creds(request)
                    logger.info('GET BASIC AUTH')
                    if not credentials_answer:
                        logger.info('NOT CREDENTIALS IN HEADER')
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
                        detail='Basic or Bearer authorize required',
                    )
                result = ldap._check_auth(server=config.fields.get('servers').get('ldap'), domain='SIGMA',
                                          login=username, password=password)
                if not result:
                    logger.info('USER NOT AUTHORIZED IN LDAP')
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='User not authorized in ldap',
                    )
            else:
                logger.info('GOT NO AUTH')
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Authorize required',
                )
            response: Response = await original_route_handler(request)

            request_status: str = 'pending'
            request_id: str = str(uuid4())
            path: str = request.url.path
            method: str = request.method

            if await request.body():
                body = await request.json()
            elif method == 'GET':
                body = dict(request.query_params)
            else:
                body = {}

            old_api_auth_token = await old_api_token(username, password)
            body['token'] = old_api_auth_token
            body = json.dumps(body)

            headers_dict.pop('authorization', None)
            headers = str(headers_dict).replace("'", '"')

            # ToDo check domain
            DB.insert_data('queue_main', request_id, path, 'sigma', username, request_status)
            DB.insert_data('queue_requests', request_id, method, path, body, headers, '')

            dt: int = settings.fake_users_db[username]["dt"]
            while dt != 0:
                result = DB.universal_select(select_done_req_with_response.format(request_id))
                if result:
                    body = {"message": result[0].status, "response": result[0].response_body}
                    response.body = str(body).encode()
                    response.body = json.dumps(body).encode()
                    response.headers['content-length'] = str(len(response.body))
                    return response

                else:
                    dt -= 1
            else:
                body = {"message": "success", "id": request_id}

            response.body = str(body).encode()
            response.body = json.dumps(body).encode()
            response.headers['content-length'] = str(len(response.body))
            return response

        return custom_route_handler


app = FastAPI()
router = APIRouter(route_class=ContextIncludedRoute)


@app.post('/token_new/')
async def login_for_access_token_new(request: Request):
    """Получить токен новый
    """
    credentials_answer = await get_creds(request)
    if not credentials_answer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Can not find auth header',
        )
    username, password = credentials_answer
    result: bool = ldap._check_auth(server=config.fields.get('servers').get('ldap'), domain='SIGMA', login=username,
                                    password=password)
    if result:
        security_string: str = username + '|' + password + '|' + '10.01.2020'
        access_token: str = await encrypt_password(security_string)
        return {'access_token': f'Bearer: {access_token}'}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect username or password',
        )


@router.post('/endpoint/')
async def publish_new_request():
    """Медленный метод для тестов"""
    for i in range(10000):
        for j in range(20000):
            b = i + j
    return {'s': 'information'}


@router.post('/bb/zxc/')
async def publish_new_request():
    """Быстрый метод для тестов"""
    return {'s': 'information'}


@router.post('/bb/qwe/')
async def publish_new_request():
    """Медленный метод для тестов"""
    for i in range(10000):
        for j in range(20000):
            b = i + j
    return {'s': 'information'}


@router.post('/bb/create_project')
async def bb_create_project(data: dict):
    logger.info('qweqew')
    return {"a": "b"}


@app.get('/queue/request/{request_id}', response_model=ResponseTemplateOut)
async def get_request(request_id: str, response: Response):
    """Получить информацию о запросе по request_uuid"""
    result: dict = DB.select_data('queue_main', 'status', param_name='request_id', param_value=request_id)
    if result:
        result = result[0]  # because fetch all
        response.status_code = status.HTTP_200_OK
        if result['status'] != 'pending':
            return {'payload': {
                'request_id': request_id,
                'status': result['status']
            }
            }
        else:
            payload = {
                'request_id': result['request_id'],
                'endpoint': result['endpoint'],
                'data': result['timestamp'],
                'author': result['login']
            }
            return ResponseTemplateOut(response_status='200 OK', message='done', payload=payload)

    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseTemplateOut(response_status='200 OK', message='zxc', payload='unluck')


@app.put('/queue/request/{request_id}')
async def update_request(request_id: str, request: Request):
    """Обновить информацию о запросе по request_id"""
    body: dict = await request.json()
    main_table = 'queue_main'
    param_name = 'request_id'
    result: dict = DB.update_data(main_table, field_name=body['field'], field_value=body['value'],
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


@router.post('/api/v3/nexus/info')
async def get_nexus_info():
    return 1


@router.get('/api/v6/bbci/project')
async def get_bb_info():
    return 1


@router.get('/api/v6/jira/project')
async def get_bb_info():
    return 1


app.include_router(router)

if __name__ == "__main__":
    parent_directory = pathlib.Path(__file__).parent.resolve()
    config_file = str(parent_directory) + config.fields.get('path').get('config')
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True, log_config=config_file)
