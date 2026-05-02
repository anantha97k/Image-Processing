import urllib.request
from functools import cache
from pathlib import Path

import boto3
from fastapi import HTTPException

from app.shared.const import bucket, cdn


@cache
def client():
    s3 = boto3.client("s3")
    try:
        yield s3
    except Exception as e:
        raise e


def aws_post_image(file, s3):
    try:
        s3.upload_fileobj(
            file.file,
            bucket,
            file.filename,
            ExtraArgs={"ACL": "public-read", "ContentType": file.content_type},
        )
    except Exception as e:
        raise e

    return True


def aws_get_image(image_name):

    if Path(f"images/{image_name}").exists():
        return

    try:
        urllib.request.urlretrieve(f"{cdn}{image_name}", f"images/{image_name}")
    except Exception as e:
        raise HTTPException(status_code=404, detail=e) from e
