from celery import Celery

image_processing = Celery(
    "tasks",
    broker="redis://localhost/0",
    backend="redis://localhost/1",
    include=["app.services.image_transform"],
)
