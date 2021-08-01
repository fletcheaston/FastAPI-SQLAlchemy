import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError, NoResultFound

from backend.models import User
from backend.schemas import UserCreate, UserFilter, UserList, UserSaved
from backend.utils import (
    AuthenticatedServer,
    UnauthenticatedServer,
    UserServer,
    as_query,
    get_password_hash,
)
from server.config import settings

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserSaved)
def create_user(
    new_user: UserCreate,
    server: UnauthenticatedServer = Depends(),
) -> Any:
    try:
        user = User(
            full_name=new_user.full_name,
            email=new_user.email,
            hashed_password=get_password_hash(new_user.password),
        )

        server.db.add(user)
        server.db.commit()
        server.db.refresh(user)

        # Automatically log the created user in.
        # FIXME: THIS IS NOT SECURE AT ALL.
        # You'll really want to create a session, use a JWT, or something else.
        # This just creates a cookie with the user's ID. Not secure at all.
        server.response.set_cookie(key=settings.COOKIE_NAME, value=user.id)

        return user

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists.",
        )


@router.get("", response_model=UserList)
def list_users(
    filters: UserFilter = Depends(as_query("filters", UserFilter)),
    server: UserServer = Depends(),
) -> Any:
    query = select(User)

    if filters.search:
        query = query.filter(User.full_name.contains(filters.search))

    total_count = server.db.execute(
        select(func.count()).select_from(query.subquery())
    ).one()[0]

    query = query.offset(filters.offset)
    query = query.limit(filters.limit)

    results = server.db.execute(query)
    scalars = results.scalars()

    users = scalars.all()

    return {
        "total_result_count": total_count,
        "results": users,
    }


@router.get("/{id}", response_model=UserSaved)
def retrieve_user(
    id: uuid.UUID,
    server: UserServer = Depends(),
) -> Any:
    try:
        query = select(User).filter(User.id == id)

        results = server.db.execute(query)
        scalars = results.scalars()

        return scalars.one()

    except NoResultFound:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this ID does not exist.",
        )


@router.delete("", response_model=None)
def delete_my_user(
    server: AuthenticatedServer = Depends(),
) -> Any:
    query = delete(User).filter(User.id == server.user.id)
    server.db.execute(query)
    server.db.commit()
