import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, declared_attr


class BaseDB:
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__.lower()  # type: ignore

    id: uuid.UUID = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        index=True,
        primary_key=True,
    )
    updated: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created: datetime = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
    )


Base = declarative_base(cls=BaseDB)
