import datetime

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from db import get_db
from base.utils import create_token, authenticate_user, check_token, LIFETIME_TOKEN_MIN
from routers_server.authorization.schemas import Token, AuthenticateData, TokenCheck
from routers_server.users.models import get_user_with_name

router_server_authorization = APIRouter(prefix='/authorization', tags=["authorization"])


@router_server_authorization.post("/check")
async def check_access_token(form_data: TokenCheck, db: Session = Depends(get_db)):
    content = dict()
    #   получаем юзера и время создания токена
    user, time_life_token = check_token(form_data.token)
    if not user or not time_life_token:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        #   достаем пользователя из бд
        user_db = await get_user_with_name(db, user)
        if not user_db:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED)
        content.update(user_id=user_db.id)

        if time_life_token:
            #   перевыдаем токен, если он наполовину жив
            if (int(time_life_token) - datetime.datetime.now().timestamp()) < \
                    (LIFETIME_TOKEN_MIN * 60) / 2:
                access_token = create_token(
                    data={"sub": user}
                )
                content.update(access_token=access_token)

        return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@router_server_authorization.post("/token", response_model=Token)
async def login_for_access_token(form_data: AuthenticateData, db: Session = Depends(get_db)):
    #   проверяем пользователя в базе
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED)
    # раз уж залогинился выдаем токен
    access_token = create_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}
