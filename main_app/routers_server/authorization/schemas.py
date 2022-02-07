from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenCheck(BaseModel):
    token: str | None


class AuthenticateData(BaseModel):
    username: str
    password: str
