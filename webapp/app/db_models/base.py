from __future__ import annotations

from typing import Any

from sqlalchemy.orm import DeclarativeBase, declared_attr

constraint_naming_conventions = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    # metadata = MetaData(naming_convention=constraint_naming_conventions)  # type: ignore

    id: Any

    # Generate __tablename__ automatically
    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa B904 pylint: disable=no-self-argument
        # sourcery skip: instance-method-first-arg-name
        return cls.__name__.lower()

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}
