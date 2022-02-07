from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str
    right_id: int

    class Config:
        orm_mode = True


class UserRight(BaseModel):
    name: str
    right_date: dict

    class Config:
        orm_mode = True
