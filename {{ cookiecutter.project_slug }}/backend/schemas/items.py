import uuid
from typing import Any, Dict, List, Optional

from pydantic import root_validator

from .base import BaseFilter, BaseIdentifier, BaseList, BaseModel, BaseSaved


class ItemSaved(BaseSaved):
    name: str
    description: str
    owner_id: uuid.UUID


class ItemCreate(BaseModel):
    name: str
    description: str


class ItemIdentifier(BaseIdentifier):
    name: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None

    @root_validator()  # TODO: This is all business logic, do I really want business logic here?
    def check_for_id_xor_owner_and_name(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # If ID is not None, ensure owner_id and name are None.
        if values.get("id") is not None:
            assert values.get("name") is None
            assert values.get("owner_id") is None

        else:
            assert values.get("name") is not None
            assert values.get("owner_id") is not None

        return values


class ItemFilter(BaseFilter):
    search: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None


class ItemList(BaseList):
    results: List[ItemSaved]
