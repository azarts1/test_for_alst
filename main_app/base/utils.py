from datetime import datetime, timedelta
import re

from fastapi import status
from fastapi.responses import JSONResponse
from jose import jwt
from passlib.context import CryptContext

from db import database
from routers_server.users.models import get_user_with_name
from routers_server.users.schemas import UserRight, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "37d7745069fb1d578b6ff142a89f22b61ad464bb33053b23032d4b4d76989e04"
ALGORITHM = "HS256"
LIFETIME_TOKEN_MIN = 2  # для наглядности


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


async def authenticate_user(db, username: str, password: str) -> User | bool:
    user = await get_user_with_name(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_token(data: dict) -> str:
    expires_delta = timedelta(minutes=LIFETIME_TOKEN_MIN)
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta

    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


#   так выглядят полные права вместе с рабочими (/docs и тд) права, регулярка в ключе для быстрого поиска
# {
# '^/openapi\\.json$': [{'method': 'HEAD', 'path_regex': '/openapi.json'},
#                       {'method': 'GET', 'path_regex': '/openapi.json'}],
# '^/docs$': [{'method': 'HEAD', 'path_regex': '/docs'}, {'method': 'GET', 'path_regex': '/docs'}],
# '^/docs/oauth2\\-redirect$': [{'method': 'HEAD', 'path_regex': '/docs/oauth2-redirect'},
#                               {'method': 'GET', 'path_regex': '/docs/oauth2-redirect'}],
# '^/redoc$': [{'method': 'HEAD', 'path_regex': '/redoc'}, {'method': 'GET', 'path_regex': '/redoc'}],
# '^/client/login$': [{'method': 'GET', 'path_regex': '/client/login'}],
# '^/client/collections$': [{'method': 'GET', 'path_regex': '/client/collections'}],
# '^/authorization/token$': [{'method': 'POST', 'path_regex': '/authorization/token'}],
# '^/server/users$': [{'method': 'GET', 'path_regex': '/server/users'},
#                     {'method': 'POST', 'path_regex': '/server/users'}],
# '^/server/users/(?P<name>[^/]+)$': [{'method': 'GET', 'path_regex': '/server/users/{name}'}],
# '^/server/users/(?P<user_id>[^/]+)$': [{'method': 'DELETE', 'path_regex': '/server/users/{user_id}'},
#                                        {'method': 'PUT', 'path_regex': '/server/users/{user_id}'}],
# '^/server/right$': [{'method': 'GET', 'path_regex': '/server/right'}]
# }
def check_right(right: UserRight, method: str, path: str) -> bool | None:
    for path_re in right.right_date.keys():
        if re.findall(path_re, path):
            for method_in_right in right.right_date[path_re]:
                if method_in_right["method"] == method:
                    return True


def check_token(token) -> tuple[str | None, int | None]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        time_life = payload.get("exp")
        return username, time_life
    except Exception:
        return None, None


async def check_valid(token, method, path) -> JSONResponse | None:
    try:
        #   проверяем токен
        username_jwt, time_life = check_token(token)
        async with database.async_session() as session:
            #   получаем данные о пользователе
            username_db = await get_user_with_name(session, username_jwt)

        if username_jwt is None or username_db is None or username_jwt != username_db.username:
            #   вернем если что-то не так
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED)

        #   проверяем есть ли у пользователя доступ
        if check_right(username_db.right, method, path) is None:
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN)
    #   если что-то опять же не так
    except Exception:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED)
