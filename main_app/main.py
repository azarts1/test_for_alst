import json
import os

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.exceptions import HTTPException
from sqlalchemy import text

from db import engine, Base
from routers_client.controllers import router_client
from routers_server.authorization.controllers import router_server_authorization
from routers_server.users.controllers import router_server_user
from base.utils import check_valid


if os.getenv("DEBUG"):
    app = FastAPI()
else:
    #   отключем доки и системыне ссылки на "проде"
    app_settings = dict(openapi_url=None, docs_url=None, redoc_url=None)
    app = FastAPI(**app_settings)

app.include_router(router_client)
app.include_router(router_server_authorization)
app.include_router(router_server_user)


# ловим 404 для удобства в тестовом
async def custom_exception_handler(request: Request, exc: HTTPException) -> RedirectResponse:
    if exc.status_code == 404:
        return RedirectResponse('/login')


app.add_exception_handler(HTTPException, custom_exception_handler)


#   смотрим на пришедший запрос
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    path = request.url.path.split('/')

    if path[1] == 'server':  # внутренние роуты требуют проверки прав
        authorization = request.headers.get('Authorization')
        #   проверям права и авторизацию
        if result := await check_valid(authorization, request.method, request.url.path):
            #   если что-то не так вернем ошибку
            return result
    return await call_next(request)


@app.on_event("startup")
async def startup():
    # Переливаем базу при каждом запуске
    full_right = {
        '^/login$': [{'method': 'GET', 'path_regex': '/client/login'}],
        '^/collections$': [{'method': 'GET', 'path_regex': '/client/collections'}],
        '^/authorization/token$': [{'method': 'POST', 'path_regex': '/authorization/token'}],
        '^/server/users$': [{'method': 'GET', 'path_regex': '/server/users'},
                            {'method': 'POST', 'path_regex': '/server/users'}],
        '^/server/users/(?P<name>[^/]+)$': [{'method': 'GET', 'path_regex': '/server/users/{name}'}],
        '^/server/users/(?P<user_id>[^/]+)$': [{'method': 'DELETE', 'path_regex': '/server/users/{user_id}'},
                                               {'method': 'PUT', 'path_regex': '/server/users/{user_id}'}],
        '^/server/right$': [{'method': 'GET', 'path_regex': '/server/right'}]
    }
    watch_right = {
        '^/login$': [{'method': 'GET', 'path_regex': '/client/login'}],
        '^/collections$': [{'method': 'GET', 'path_regex': '/client/collections'}],
        '^/authorization/token$': [{'method': 'POST', 'path_regex': '/authorization/token'}],
        '^/server/users$': [{'method': 'GET', 'path_regex': '/server/users'}],
        '^/server/users/(?P<name>[^/]+)$': [{'method': 'GET', 'path_regex': '/server/users/{name}'}],
        '^/server/right$': [{'method': 'GET', 'path_regex': '/server/right'}]
    }
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        query_add_right = text("""
            insert into users_right (name, right_date) values
            ('Full Admin', :full_r ),
            ('Watching Admin', :watch_r)
        """)
        await conn.execute(query_add_right,
                           dict(full_r=json.dumps(full_right), watch_r=json.dumps(watch_right)))
        await conn.execute(text("""
            insert into users (username, password, right_id) values
            ('admin', '$2b$12$JSSqTr021Y40ja0YB.4f5u.d0Aw/EnfQV3scCwpxGtVufJatPatza', 1),
            ('admin1', '$2b$12$JSSqTr021Y40ja0YB.4f5u.d0Aw/EnfQV3scCwpxGtVufJatPatza', 2)
        """))

#   фунция котороя отдает полнейшие права, настройти прав нет, так что она ни к чему
# def all_route():
#     result = dict()
#     for route in app.routes:
#         for method in route.methods:
#             if route.path_regex.pattern in result:
#                 result[route.path_regex.pattern].append(dict(method=method, path_regex=route.path))
#             else:
#                 result[route.path_regex.pattern] = list()
#                 result[route.path_regex.pattern].append(dict(method=method, path_regex=route.path))
#     return result
