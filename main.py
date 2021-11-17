from datetime import datetime
from typing import Callable, Optional
from uuid import uuid4
from datetime import timedelta,timezone, date as datezxc

from fastapi import Depends, FastAPI, HTTPException, status, Request, Response, APIRouter
from fastapi.routing import APIRoute
import fastapi

from models import Token, User
from security import OAuth2PasswordRequestForm, authenticate_user, fake_users_db, ACCESS_TOKEN_EXPIRE_MINUTES, \
    create_access_token, get_current_active_user, encrypt_password, decrypt_password, InvalidToken
from DBConnector import insert_data, get_request_by_uuid, update_request_by_uuid, get_queue_statistics


class ContextIncludedRoute(APIRoute):
    """
    Класс-роутер, обрабатывающий запросы, требующие добавления информации в базу данных
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            queue_id = str(uuid4())
            path = request.url.path
            params = request.path_params
            user = 'qwe'
            status = 'new'
            if request.headers.get('auth'):
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
                if username in fake_users_db:
                    if username not in fake_users_db[username]['username'] or password not in fake_users_db[username]['password']:
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

            time = datetime.now().time()
            date = datezxc.today()
            print(time)
            print(date)
            timestamp = datetime.now()

            body = await request.body()
            body = body.decode("utf-8")

            print(body)
            if body:
                insert_data(queue_id, path, body, user, status, date, time, timestamp)
            else:
                insert_data(queue_id, path, None, user, status, date, time, timestamp)

            print(queue_id, path, params, user, status, date, time, timestamp)

            return response

        return custom_route_handler


app = FastAPI()
router = APIRouter(route_class=ContextIncludedRoute)


@app.post('/token/', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Получить токен
    """
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.post('/token_new/')
async def login_for_access_token_new(request: Request):
    """Получить токен новый
    """
    body = await request.json()
    username = body['username']
    password = body['password']
    if username in fake_users_db[username]['username'] and password in fake_users_db[username]['password']:
        security_string = username + '|' + password + '|' + '10.01.2020'
        access_token = await encrypt_password(security_string)
        return {'access_token': access_token}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )


@app.get('/users/me/', response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Получить информацию о теккущем пользователе
    """
    return current_user


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


@app.get('/users/me/items/')
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    """Получить дополнительную информацию о текущем пользователе
    """
    return [{'item_id': 'Foo', 'owner': current_user.username}]


@app.post('/bb/create_project')
async def bb_create_project(data: dict):
    queue_id = str(uuid4())
    endpoint = '/bb/create_project'
    author = 'cab-sa-mls00001'
    status = 'new'
    data = str(data).replace("'", '"')
    time = datetime.strftime(datetime.now(), '%H:%M:%S')
    date = datetime.strftime(datetime.now(), '%d.%m.%Y')
    timestamp = '10-10-10'
    insert_data(queue_id, endpoint, data, author, status, date, time, timestamp)
    return {'l':'b'}


@app.get('/queue/{request_uuid}')
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


@app.put('/queue/{request_uuid}')
async def update_request(request_uuid: str, request: Request):
    """Обновить информацию о запросе по uuid"""
    body = await request.json()
    result = update_request_by_uuid(request_uuid, body['field'], body['value'])
    return result


@app.get('/queue/')
async def get_queue_info(status: Optional[str] = None, period: Optional[str] = None, endpoint: Optional[str] = None, directory: Optional[str] = None):
    """Получить информацию об очереди"""
    result = get_queue_statistics(status=status, period=period,endpoint=endpoint,directory=directory)
    return result


app.include_router(router)
