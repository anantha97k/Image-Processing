from pydantic import BaseModel


# Pydantic
class UserForm(BaseModel):
    uid: int | None = None
    username: str


class UserInDB(UserForm):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    uid: int | None = None
