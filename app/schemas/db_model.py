from typing import List

from sqlalchemy import ForeignKey, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)


class Base(DeclarativeBase):
    pass


# ORM
class Users(Base):
    __tablename__ = "users"
    uid: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(10), unique=True)
    password: Mapped[str] = mapped_column(String(10))
    images: Mapped[List["Images"]] = relationship(back_populates="user")


class Images(Base):
    __tablename__ = "images"
    img_id: Mapped[int] = mapped_column(primary_key=True)
    image_name: Mapped[str] = mapped_column(String, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.uid"))
    user: Mapped["Users"] = relationship(back_populates="images")


DATABASE_URL = (
    "postgresql+psycopg2://kumar97:@localhost:5432/"
    "image?options=-csearch_path%3Dusers,public"
)

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, bind=engine, autoflush=False)
