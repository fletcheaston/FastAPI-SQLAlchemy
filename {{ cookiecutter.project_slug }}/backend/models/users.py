from typing import TYPE_CHECKING, List

from sqlalchemy import Column, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from .items import Item  # noqa: F401


class User(Base):
    full_name: str = Column(
        Text,
        nullable=False,
    )
    email: str = Column(
        Text,
        index=True,
        unique=True,
        nullable=False,
    )
    hashed_password: str = Column(
        Text,
        nullable=False,
    )

    items: List["Item"] = relationship(
        "Item",
        back_populates="owner",
    )

    __table_args__ = (UniqueConstraint(email),)
