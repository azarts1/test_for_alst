from sqlalchemy import Column, ForeignKey, Integer, VARCHAR, Text, JSON
from sqlalchemy.orm import Session, relationship, joinedload, load_only

from sqlalchemy import select, update, delete, insert

from db import Base
from routers_server.users.schemas import User


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(VARCHAR(15), unique=True, nullable=False)
    password = Column(Text(), nullable=False)
    right_id = Column(Integer, ForeignKey('users_right.id'), nullable=False)

    right = relationship("UsersRight", backref="users", lazy='joined')

    __table_args__ = {'extend_existing': True}


async def get_user_with_name(db: Session, username: str) -> User:
    query = select(Users).where(Users.username == username)
    result = await db.execute(query)
    result = result.scalars().first()
    return result


async def get_user_with_id(db: Session, user_id: int) -> User:
    query = select(Users).where(Users.id == user_id)
    result = await db.execute(query)
    result = result.scalars().first()
    return result


async def all_user(db: Session) -> list[User]:
    query = select(Users).options(load_only(Users.username), joinedload(Users.right)).order_by(Users.id)
    result = await db.execute(query)
    result = result.scalars().all()
    return result


async def user_delete(db: Session, user_id: int) -> None:
    query = delete(Users).where(Users.id == user_id)
    await db.execute(query)


async def user_add(db: Session, user: User) -> User:
    query = insert(Users).values(user.dict())
    await db.execute(query)
    result = await get_user_with_name(db, user.username)
    return result


async def update_user(db: Session, new_data_user: User, user_id: int) -> User:
    query = update(Users).values(new_data_user.dict()).where(Users.id == user_id)
    await db.execute(query)
    result = await get_user_with_name(db, new_data_user.username)
    return result


class UsersRight(Base):
    __tablename__ = "users_right"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(20), nullable=False)
    right_date = Column(JSON)

    __table_args__ = {'extend_existing': True}


async def all_right(db: Session):
    query = select(UsersRight)
    result = await db.execute(query)
    result = result.scalars().all()
    return result
