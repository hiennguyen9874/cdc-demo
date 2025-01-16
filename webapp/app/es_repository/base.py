from typing import ParamSpec, TypeVar

Param = ParamSpec("Param")
RetType = TypeVar("RetType")


class BaseESRepository:  # noqa: B903
    metrics_histogram: list[tuple[str, str]] = []

    def __init__(self, index_name: str) -> None:
        self.index_name = index_name
