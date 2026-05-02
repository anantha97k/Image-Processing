from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    uid: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(10), unique=True)
    password: Mapped[str] = mapped_column(String(10))


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

Base.metadata.create_all(bind=engine)  # Bind the engine

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
