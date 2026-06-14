from fastapi import (
    FastAPI,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# Routers
from app.routers import auth_router, image_router


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


origins = ["*"]

templates = Jinja2Templates(directory="web")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.auth_router)
app.include_router(image_router.image_router)


@app.exception_handler(HTTPException)
async def unicorn_exception_handler(exc: HTTPException):
    print(exc.status_code)
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


@app.get("/")
async def test():
    return FileResponse("web/index.html")
