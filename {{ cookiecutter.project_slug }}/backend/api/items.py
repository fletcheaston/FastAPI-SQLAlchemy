import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError, NoResultFound

from backend.models import Item
from backend.schemas import ItemCreate, ItemFilter, ItemList, ItemSaved
from backend.utils import AuthenticatedServer, UserServer, as_query

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("", response_model=ItemSaved)
def create_item(
    new_item: ItemCreate,
    server: AuthenticatedServer = Depends(),
) -> Any:
    try:
        item = Item(
            name=new_item.name,
            description=new_item.description,
            owner=server.user,
        )

        server.db.add(item)
        server.db.commit()
        server.db.refresh(item)

        return item

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this item already exists.",
        )


@router.get("", response_model=ItemList)
def list_items(
    filters: ItemFilter = Depends(as_query("filters", ItemFilter)),
    server: UserServer = Depends(),
) -> Any:
    query = select(Item)

    if filters.search:
        query = query.filter(search_vector=filters.search)

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


@router.get("/{id}", response_model=ItemSaved)
def retrieve_item(
    id: uuid.UUID,
    server: UserServer = Depends(),
) -> Any:
    try:
        query = select(Item).filter(Item.id == id)

        results = server.db.execute(query)
        scalars = results.scalars()

        return scalars.one()

    except NoResultFound:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item with this ID does not exist.",
        )


@router.delete("/{id}", response_model=None)
def delete_item(
    id: uuid.UUID,
    server: AuthenticatedServer = Depends(),
) -> Any:
    query = delete(Item).filter(Item.id == id, Item.owner_id == server.user.id)
    server.db.execute(query)
    server.db.commit()
