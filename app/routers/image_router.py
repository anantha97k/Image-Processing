import asyncio

# Auth
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# DB
from sqlalchemy.orm import Session

# Models
from app.schemas.form__model import UserForm
from app.schemas.image_model import Transform
from app.services.auth import get_current_user
from app.services.db_crud import get_image, post_image

# Celery task
from app.services.image_transform import transform_image_task

# Rate limiter
from app.services.limit import custom_limiter

# AWS
from app.shared.aws import client

# CONSTS
from app.shared.const import cdn
from app.shared.db_conn import get_db

templates = Jinja2Templates(directory="web")

auth_router = APIRouter()


image_router = APIRouter(prefix="/images", tags=["images"])


@image_router.post("/")
async def upload_image(
    current_user: Annotated[UserForm, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    s3=Depends(client),
    file: UploadFile = File(...),
):
    try:
        post_image(file, current_user.uid, db, s3)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e,
        ) from e

    return RedirectResponse(
        url=f"/auth/home/@{current_user.username}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@image_router.get("/{uid}", dependencies=[Depends(get_current_user)])
async def get_image_id(
    uid: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):

    image = get_image(uid, db)

    if image:
        return templates.TemplateResponse(
            request=request,
            name="image_id.html",
            context={"image": image, "url": f"{cdn}{image.image_name}"},
        )

    return HTTPException(
        status_code=404,
    )


@image_router.post("/{uid}/transform", dependencies=[Depends(get_current_user)])
@custom_limiter
async def post_image_transformation(
    request: Request,
    transform: Transform,
    uid: int,
    db: Annotated[Session, Depends(get_db)],
):
    image_json = transform.model_dump()
    image_aws = get_image(uid, db)
    if image_aws:
        image = transform_image_task.delay(image_json, image_aws.image_name)
        await asyncio.sleep(1)
        if image.result:
            return FileResponse(
                path=image.result["path"],
                filename=image.result["filename"],
                media_type=f"image/{transform.format}",
            )
