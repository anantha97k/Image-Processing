from pydantic import BaseModel


class Resize(BaseModel):
    width: int
    height: int


class Crop(BaseModel):
    x: float
    y: float
    width: float
    height: float


class Filters(BaseModel):
    grayscale: bool = False
    sepia: bool = False


class Transform(BaseModel):
    resize: Resize
    crop: Crop
    rotate: int
    format: str
    filters: Filters
