from typing import Any, Generic, ParamSpec, Sequence, Type, TypeVar

from sqlalchemy import delete, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.db_models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
Param = ParamSpec("Param")
RetType = TypeVar("RetType")


class BaseDbRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    ## Create

    async def create(self, db: AsyncSession, *, db_obj: ModelType) -> ModelType:
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def creates(self, db: AsyncSession, *, db_objs: list[ModelType]) -> None:
        for db_obj in db_objs:
            db.add(db_obj)
        await db.commit()

    ## Get multi

    async def get_multi(
        self, db: AsyncSession, *, offset: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        query = select(self.model).offset(offset).limit(limit).order_by(self.model.id)
        q = await db.execute(query)
        return q.scalars().all()

    async def get_multi_count(
        self, db: AsyncSession, *, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[ModelType], int]:
        items = await self.get_multi(db, offset=offset, limit=limit)
        total = await self.count_all(db)
        return items, total

    ## Get all

    async def get_all(self, db: AsyncSession) -> Sequence[ModelType]:
        query = select(self.model).order_by(self.model.id)
        q = await db.execute(query)
        return q.scalars().all()

    ## Get one

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        q = await db.execute(select(self.model).where(self.model.id == id))
        return q.scalars().one_or_none()

    def get_sync(self, db: Session, id: Any) -> ModelType | None:
        q = db.execute(select(self.model).where(self.model.id == id))
        return q.scalars().one_or_none()

    ## Count

    async def count(self, db: AsyncSession, query: Select) -> int:
        """Counting of results returned by the query

        Args:
            db (AsyncSession): AsyncSession
            query (Select): query

        Returns:
            int: Number of results returned by the query
        """
        return await db.scalar(
            select(func.count()).select_from(
                query.with_only_columns(self.model.id).subquery()  # type: ignore
            )
        )

    async def count_all(self, db: AsyncSession) -> int:
        return await self.count(db=db, query=select(self.model))

    def count_sync(self, db: Session, query: Select) -> int:
        """Counting of results returned by the query

        Args:
            db (AsyncSession): AsyncSession
            query (Select): query

        Returns:
            int: Number of results returned by the query
        """
        return db.scalar(
            select(func.count()).select_from(
                query.with_only_columns(self.model.id).subquery()  # type: ignore
            )
        )

    ## Delete

    async def delete_by_id(self, db: AsyncSession, *, id: int) -> ModelType | None:
        q = await db.execute(select(self.model).where(self.model.id == id))
        obj = q.scalar_one()
        await db.delete(obj)
        await db.commit()
        return obj

    def delete_by_ids_sync(self, db: Session, ids: list[int]) -> None:
        query = delete(self.model).where(self.model.id.in_(list(ids)))
        db.execute(query)
        db.commit()

    async def delete(self, db: AsyncSession, *, db_obj: ModelType) -> None:
        await db.delete(db_obj)
        await db.commit()

    def delete_sync(self, db: Session, *, db_obj: ModelType) -> None:
        db.delete(db_obj)
        db.commit()

    ## Update

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        update_data: dict[str, Any],
    ) -> ModelType:
        query = update(self.model).where(self.model.id == db_obj.id).values(update_data)
        await db.execute(query)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
