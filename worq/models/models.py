from sqlalchemy import Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from .meta import Base

Base = declarative_base()
metadata = Base.metadata

class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String(255))
