from typing import List, Optional

from pydantic import EmailStr

from .base import BaseFilter, BaseIdentifier, BaseList, BaseModel, BaseSaved


class UserSaved(BaseSaved):
    full_name: str
    email: EmailStr


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserIdentifier(BaseIdentifier):
    email: Optional[EmailStr] = None


class UserFilter(BaseFilter):
    search: Optional[str] = None


class UserList(BaseList):
    results: List[UserSaved]


class UserLogin(BaseModel):
    email: EmailStr
    password: str
