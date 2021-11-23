from datetime import datetime
from typing import Callable, Optional
from uuid import uuid4
import base64

from fastapi import FastAPI, HTTPException, status, Request, Response, APIRouter
from fastapi.routing import APIRoute
import fastapi

from core.services.security import decrypt_password, encrypt_password, InvalidToken
from core.settings import settings
from core.connectors import LDAP

from core.services.db_service import insert_data, get_request_by_uuid, get_queue_statistics, update_request_by_uuid


class ContextIncludedRoute(APIRoute):
    """
    Класс-роутер, обрабатывающий запросы, требующие добавления информации в базу данных
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            headers = dict(request.headers)
            if headers.get('auth'):
                try:
                    data = await decrypt_password(request.headers['Auth'])
                except InvalidToken:
                    raise HTTPException(
                        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                        detail='Invalid token',
                        headers={'WWW-Authenticate': 'Bearer'},
                    )
                username, password, date = data.split('|')
                print(username, password, date)
                if username in settings.fake_users_db:
                    if username not in settings.fake_users_db[username]['username'] or\
                            password not in settings.fake_users_db[username]['password']:
                        raise HTTPException(
                            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                            detail='Incorrect username or password',
                            headers={'WWW-Authenticate': 'Bearer'},
                        )
                else:
                    raise HTTPException(
                        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                        detail='Incorrect username or password',
                        headers={'WWW-Authenticate': 'Bearer'},
                    )
            response: Response = await original_route_handler(request)

            if response.status_code != 200:
                print('Unexpected error')
                return response

            user = 'qwe'
            status = 'new'
            queue_id = str(uuid4())
            path = request.url.path
            method = request.method
            timestamp = str(datetime.now())
            body = await request.body()
            body = body.decode("utf-8")
            headers_for_insert = str(headers).replace("'", '"')

            insert_data('queue_main', queue_id, path, user, timestamp, status, '0', '0', 'sigma')
            insert_data('queue_requests', queue_id, method, path, body, headers_for_insert, '', timestamp)

            return response

        return custom_route_handler


app = FastAPI()
router = APIRouter(route_class=ContextIncludedRoute)


    # {
    #     status:''
    #     message:''
    #     *errors:[]
    #     payload:{}
    # }


@app.post('/token_new/')
async def login_for_access_token_new(request: Request):
    """Получить токен новый
    """
    REQ = await request.json()
    creds = REQ.headers.get("auth")
    creds = base64.b64decode(creds.replace('Basic ', '')).decode().split(":")
    
    username = creds[0]  # body['username']
    password = creds[1]  # body['password']
    
    if LDAP.auth_user(*creds): 
        security_string = username + '|' + password + '|' + '10.01.2020'
        access_token = await encrypt_password(security_string)
        return {'access_token': access_token}

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
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
    """Медленный метод для тестов"""
    for i in range(10000):
        for j in range(20000):
            b = i + j
    return {'s': 'information'}


@router.post('/bb/qwe/')
async def publish_new_request():
    """Медленный метод для тестов"""
    for i in range(10000):
        for j in range(20000):
            b = i + j
    return {'s': 'information'}


@app.post("/bb/create_project")
async def bb_create_project(request: Request, data: dict):#, current_user: User = Depends(get_current_user)):
    queue_id = str(uuid.uuid4())
    endpoint = request.scope["path"]
    author = 'johndoe'#current_user.username
    domain = data.get('domain')
    status = 'PENDING'
    priority = '1'
    work_count = '0'
    request_type = request.method
    request_url = request.scope["path"]
    data = str(data).replace("'", '"')
    headers = {}
    for header in request.scope["headers"]:
        headers.update({header[0].decode("utf-8"): header[1].decode("utf-8")})
    headers = str(headers).replace("'", '"')

    db.insert_data('queue_main', queue_id, endpoint, domain, author, status, priority, work_count)
    db.insert_data('queue_requests', queue_id, request_type, request_url, data, headers, "")

    dt = fake_users_db[author]["dt"]
    while dt != 0:
        result = universal_select(select_done_req_id_with_response.format(queue_id))
        # result = db.select_data('queue_main', 'rqid', 'status', param_name='rqid', param_value=queue_id)[0]
        # if result.status in ("DONE", "ERROR"):
        if result:
            # response_result = db.select_data('queue_responses', 'rqid', 'response_body', param_name='rqid', param_value=queue_id)[0]
            return {"message": result[0].status, "response": result[0].response_body}
        else:
            dt -= 1
            sleep(1)
    else:
        return {"message": "success", "id": queue_id}


@app.get('/queue/request/{request_uuid}')
async def get_request(request_uuid: str, response: Response):
    """Получить информацию о запросе по uuid"""
    result = get_request_by_uuid(request_uuid)
    if result:
        response.status_code = status.HTTP_200_OK
        if result['status'] != 'finished':
            return {
                'uuid': request_uuid,
                'status': result['status']
            }
        else:
            return {
                'uuid': result['uuid'],
                'endpoint': result['endpoint'],
                'data': result['data'],
                'author': result['author']
            }
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'uuid': request_uuid}


@app.put('/queue/request/{request_uuid}')
async def update_request(request_uuid: str, request: Request):
    """Обновить информацию о запросе по uuid"""
    body = await request.json()
    result = update_request_by_uuid(request_uuid, body['field'], body['value'])
    return result


@app.get('/queue/info')
async def get_queue_info(status: Optional[str] = None, period: Optional[str] = None, endpoint: Optional[str] = None,
                         directory: Optional[str] = None):
    """Получить информацию об очереди"""
    result = get_queue_statistics(status=status, period=period, endpoint=endpoint, directory=directory)
    return result


@app.get('/queue/processing_info')
async def get_queue_info(status: Optional[str] = None, period: Optional[str] = None, endpoint: Optional[str] = None,
                         directory: Optional[str] = None):
    """Получить информацию об очереди"""
    pass


app.include_router(router)
