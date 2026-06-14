from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

# DB
from sqlalchemy.orm import Session

# Pydantic
from app.schemas.form__model import UserForm, UserInDB

# Auth
from app.services.auth import authenticate_user, create_access_token, get_current_user
from app.services.db_crud import get_images, post_user

# CONSTS
from app.shared.const import ACCESS_TOKEN_EXPIRE_MINUTES, url
from app.shared.db_conn import get_db

templates = Jinja2Templates(directory="web")

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/login", response_class=FileResponse)
async def login_get():
    return FileResponse("web/login.html")


@auth_router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if user:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.uid)}, expires_delta=access_token_expires
        )

        response = RedirectResponse(
            url=f"/auth/home/@{user.username}", status_code=status.HTTP_303_SEE_OTHER
        )

        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@auth_router.get("/home/@{username}")
async def homepage(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserForm, Depends(get_current_user)],
):

    user = get_images(current_user.uid, db)

    return templates.TemplateResponse(
        request=request, name="image_list.html", context={"user": user, "url": url}
    )


@auth_router.get("/signup", response_class=FileResponse)
async def signup_get():
    return FileResponse("web/signup.html")


@auth_router.post("/signup")
async def add_user(
    item: Annotated[UserInDB, Form()], db: Annotated[Session, Depends(get_db)]
):
    new_user_id = post_user(db, item)
    if new_user_id is False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(new_user_id)}, expires_delta=access_token_expires
    )
    response = RedirectResponse(
        url=f"/auth/home/@{item.username}", status_code=status.HTTP_303_SEE_OTHER
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response
