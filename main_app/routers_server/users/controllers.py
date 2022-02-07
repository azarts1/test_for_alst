from fastapi import Depends, status, APIRouter
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from base.utils import get_password_hash
from db import get_db
from routers_server.users.models import all_user, user_delete, all_right, user_add, update_user, get_user_with_name, get_user_with_id
from routers_server.users.schemas import User

router_server_user = APIRouter(prefix='/server', tags=["server"])


@router_server_user.get("/users")
async def get_all_users(db: Session = Depends(get_db)) -> list[User]:
    result = await all_user(db)
    return result


@router_server_user.get("/users/{name}")
async def get_users_name(name: str, db: Session = Depends(get_db)) -> User:
    result = await get_user_with_name(db, name)
    return result


@router_server_user.get("/users/{user_id}")
async def get_users_id(user_id: int, db: Session = Depends(get_db)) -> User:
    result = await get_user_with_id(db, user_id)
    return result


@router_server_user.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    result = await user_delete(db, user_id)
    return result


@router_server_user.post("/users")
async def post_user(user: User, db: Session = Depends(get_db)) -> User | JSONResponse:
    if await get_user_with_name(db, user.username):
        return JSONResponse(status_code=status.HTTP_409_CONFLICT)
    user.password = get_password_hash(user.password)
    result = await user_add(db, user)
    return result


#   пут так же добавляет но на "фронте" никак не протестить
@router_server_user.put("/users/{user_id}")
async def put_user(user: User, user_id: int, db: Session = Depends(get_db)):
    old_user = await get_user_with_id(db, user_id)
    if old_user:
        user.password = get_password_hash(user.password)
        try:
            result = await update_user(db, user, user_id)
        except:
            return JSONResponse(status_code=status.HTTP_409_CONFLICT)
        return result
    else:
        return await post_user(user, db)


@router_server_user.get("/right")
async def right(db: Session = Depends(get_db)):
    result = await all_right(db)
    return result
