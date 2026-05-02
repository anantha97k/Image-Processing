from sqlalchemy import insert, select
from sqlalchemy.orm import joinedload

from app.schemas.db_model import Images, Users
from app.schemas.form__model import UserInDB
from app.shared.aws import aws_post_image


# User
def get_user(db, username):
    query = select(Users).where(Users.username == username)
    user = db.scalars(query).first()
    if user:
        return user
    return None


def post_user(db, item: UserInDB):
    user = get_user(db, item.username)
    if user is None:
        new_user = Users(username=item.username, password=item.password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user.uid
    return False


# /image
def post_image(file, uid, db, s3):
    query = insert(Images).values(image_name=file.filename, user_id=uid)
    db.execute(query)
    db.commit()
    aws_post_image(file, s3)


def get_images(uid, db):
    query = select(Users).options(joinedload(Users.images)).filter(Users.uid == uid)
    rows = db.execute(query).unique().first()
    if rows:
        user = Users(
            uid=rows.Users.uid, username=rows.Users.username, images=rows.Users.images
        )
        return user
    return None


def get_image(image_id, db):
    image_query = select(Images).where(Images.img_id == image_id)
    image = db.scalars(image_query).first()
    if image:
        return image
    return None
