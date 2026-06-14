import uuid

from PIL import Image

from app.services.celery import image_processing
from app.shared.aws import aws_get_image

sepia_matrix = (
    0.393,
    0.769,
    0.189,
    0,  # Red channel
    0.349,
    0.686,
    0.168,
    0,  # Green channel
    0.272,
    0.534,
    0.131,
    0,  # Blue channel
)


@image_processing.task
def transform_image_task(transform: dict, image_name):
    aws_get_image(image_name)
    image = Image.open(f"images/{image_name}")
    if transform["resize"]["width"] > 0 and transform["resize"]["width"] > 0:
        image = image.resize(
            (transform["resize"]["width"], transform["resize"]["height"])
        )

    if transform["crop"]["width"] > 0 and transform["crop"]["height"] > 0:
        image = image.crop(
            (
                transform["crop"]["x"],
                transform["crop"]["y"],
                transform["crop"]["x"] + transform["crop"]["width"],
                transform["crop"]["y"] + transform["crop"]["height"],
            )
        )

    if transform["rotate"] > 0:
        image = image.rotate(transform["rotate"])

    if transform["filters"]["grayscale"]:
        image = image.convert("L")
    elif transform["filters"]["sepia"]:
        image = image.convert("RGB", sepia_matrix)

    name = uuid.uuid4()
    filename = f"{name}.{transform['format']}"
    path = f"images/{filename}"
    image.save(path)

    return {"path": path, "filename": filename}
