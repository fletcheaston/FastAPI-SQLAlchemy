import uuid

from sqlalchemy import Column, ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base
from .users import User


class Item(Base):  # type: ignore
    name: str = Column(
        Text,
        nullable=False,
    )
    description = Column(
        Text,
        nullable=False,
    )

    owner_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "user.id",
            ondelete="CASCADE",
        ),
    )
    owner: User = relationship(
        User,
        back_populates="items",
    )

    __table_args__ = (
        Index("owner_id_index", owner_id),
        UniqueConstraint(name, owner_id),
    )
