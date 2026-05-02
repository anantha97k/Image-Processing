from datetime import datetime, timedelta, timezone
from typing import Annotated

# aUTH
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select

from app.schemas.form__model import TokenData, UserForm, UserInDB

# Pydantic
from app.schemas.db_model import Users
from app.shared.const import ALGORITHM, SECRET_KEY

# DB
from app.shared.db_conn import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# GET USER
def get_user(db, username: str | None):
    query = select(Users).where(Users.username == username)
    user = db.scalars(query).first()
    if user:
        return UserInDB(**user.__dict__)
    return None


# GET ID
def get_uid(db, uid: int | None):
    query = select(Users).where(Users.uid == uid)
    user = db.scalars(query).first()
    if user:
        return UserInDB(**user.__dict__)
    return None


def authenticate_user(db, username, password):
    user = get_user(db, username)
    if not user:
        return False
    if user.password != password:
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request, db=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    token = request.cookies.get("access_token")
    if token is None:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(uid=user_id)
    except InvalidTokenError:
        raise credentials_exception from InvalidTokenError
    user = get_uid(db, uid=token_data.uid)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserForm, Depends(get_current_user)],
):
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user
