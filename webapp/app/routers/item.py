from typing import Annotated, Any

from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination.api import create_page, resolve_params
from fastapi_pagination.default import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from app import db_models, db_repository, es_repository, schemas
from app.deps import get_async_db, get_async_es
from app.utils import get_limit_offset, get_params

router = APIRouter()

Db = Annotated[AsyncSession, Depends(get_async_db)]
Es = Annotated[AsyncElasticsearch, Depends(get_async_es)]


@router.post("/", response_model=schemas.Item)
async def create_item(
    *,
    db: Db,
    item_in: schemas.ItemCreate,
) -> Any:
    """
    Create new item.
    """

    obj_in_data = item_in.model_dump(exclude_unset=True)
    db_obj = db_models.Item(**obj_in_data)  # type: ignore
    item = await db_repository.item_db_repository.create(db=db, db_obj=db_obj)
    return item


@router.get("/", response_model=Page[schemas.Item])
async def read_items(
    *,
    db: Db,
    params: Annotated[Params, Depends(get_params)],
) -> Any:
    """
    Retrieve items.
    """
    params = resolve_params(params)  # type: ignore
    limit, offset = get_limit_offset(params)

    items, total = await db_repository.item_db_repository.get_multi_count(
        db, offset=offset, limit=limit
    )
    return create_page(items, total, params)


@router.get("/get-es-items", response_model=list[schemas.Item])
async def get_es_items(
    *,
    es: Es,
) -> Any:
    """
    Retrieve items.
    """
    print(await es_repository.item.get_all(es=es))
    return await es_repository.item.get_all(es=es)


@router.get("/{id}", response_model=schemas.Item)
async def read_item(
    *,
    db: Db,
    id: int,
) -> Any:
    """
    Get item by ID.
    """
    item = await db_repository.item_db_repository.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="item not found")
    return item


@router.put("/{id}", response_model=schemas.Item)
async def update_item(
    *,
    db: Db,
    id: int,
    item_in: schemas.ItemUpdate,
) -> Any:
    """
    Update an item.
    """
    item = await db_repository.item_db_repository.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="item not found")
    item = await db_repository.item_db_repository.update(
        db=db, db_obj=item, update_data=item_in.dict(exclude_unset=True)
    )
    return item


@router.delete("/{id}", response_model=schemas.Item)
async def delete_item(
    *,
    db: Db,
    id: int,
) -> Any:
    """
    Delete an item.
    """
    item = await db_repository.item_db_repository.get(db=db, id=id)

    if not item:
        raise HTTPException(status_code=404, detail="item not found")

    await db_repository.item_db_repository.delete_by_id(db=db, id=id)

    return item
