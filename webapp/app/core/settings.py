from functools import cached_property, lru_cache
from pathlib import Path
from typing import Any, Tuple, Type

from pydantic import BaseModel, computed_field, Field, PostgresDsn, ValidationInfo
from pydantic.functional_validators import field_validator
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)
from typing_extensions import Annotated

YAML_FILE_PATH = "/app/app/configs/config.yml"


class AppSettings(BaseModel):
    CONFIG_DIR: Path = Path("/app/app/configs/")
    TIMEZONE: str = "Asia/Ho_Chi_Minh"


class SQLAlchemySettings(BaseModel):
    ECHO: bool = False

    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 5
    POOL_TIMEOUT: int = 60


class DbSettings(BaseModel):
    HOST: str = "postgres"
    PORT: int = 5432
    USER: str
    PASSWORD: str
    DB: str
    DATABASE_URI: Annotated[PostgresDsn | None, Field(validate_default=True)] = None

    @field_validator("DATABASE_URI", mode="after")
    @classmethod
    def assemble_db_connection(  # pylint: disable=no-self-argument
        cls, v: str | None, info: ValidationInfo
    ) -> Any:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql",
            username=info.data["USER"],
            password=info.data["PASSWORD"],
            host=info.data["HOST"],  # type: ignore
            port=info.data["PORT"],
            path=str(info.data["DB"]) or "",
        )

    @computed_field  # type: ignore[misc]
    @cached_property
    def ASYNC_DATABASE_URI(self) -> str:
        if not self.DATABASE_URI:
            raise RuntimeError("DATABASE_URI must be not None")

        return (
            str(self.DATABASE_URI).replace("postgresql://", "postgresql+asyncpg://")
            if self.DATABASE_URI
            else str(self.DATABASE_URI)
        )


class EsSettings(BaseModel):
    HOST: str = "es"
    PORT: str = "9200"

    @computed_field  # type: ignore[misc]
    @cached_property
    def URL(self) -> str:
        return f"http://{self.HOST}:{self.PORT}"

    TIMEOUT: int = 20
    RETRY_ON_TIMEOUT: bool = True
    MAX_RETRIES: int = 10
    CONNECTIONS_PER_NODE: int = 10

    NUMBER_OF_SHARDS: int = 1
    NUMBER_OF_ROUTING_SHARDS: int = 1

    WATERMARK_LOW: str = "5gb"
    WATERMARK_HIGH: str = "2gb"
    WATERMARK_FLOOD_STAGE: str = "1gb"


class Settings(BaseSettings):
    @classmethod
    def settings_customise_sources(  # type: ignore
        cls, settings_cls: Type[BaseSettings], **kwargs
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        global YAML_FILE_PATH

        return (
            EnvSettingsSource(
                settings_cls,
                env_nested_delimiter="__",
                env_parse_none_str="null",
                case_sensitive=False,
            ),
            YamlConfigSettingsSource(settings_cls, yaml_file=YAML_FILE_PATH),
        )

    APP: AppSettings = AppSettings()
    SQLALCHEMY: SQLAlchemySettings = SQLAlchemySettings()
    DB: DbSettings
    ES: EsSettings = EsSettings()


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
