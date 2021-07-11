from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from backend.models import User
from backend.schemas import UserLogin, UserSaved
from backend.utils import AuthenticatedServer, UnauthenticatedServer, verify_password
from server.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("", response_model=UserSaved)
def check_if_logged_in(
    server: AuthenticatedServer = Depends(),
) -> Any:
    return server.user


@router.post("", response_model=UserSaved)
def login(
    user_login: UserLogin,
    server: UnauthenticatedServer = Depends(),
) -> Any:
    try:
        query = select(User).filter(User.email == user_login.email)

        results = server.db.execute(query)
        scalars = results.scalars()

        user = scalars.one()

        assert verify_password(
            plain_password=user_login.password, hashed_password=user.hashed_password
        )

        # FIXME: THIS IS NOT SECURE AT ALL.
        # You'll really want to create a session, use a JWT, or something else.
        # This just creates a cookie with the user's ID. Not secure at all.
        server.response.set_cookie(key=settings.COOKIE_NAME, value=user.id)

        return user

    except (NoResultFound, AssertionError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials.",
        )


@router.delete("", response_model=None)
def logout(
    server: AuthenticatedServer = Depends(),
) -> Any:
    server.response.delete_cookie(key=settings.COOKIE_NAME)
