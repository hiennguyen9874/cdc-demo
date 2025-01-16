from elasticsearch import AsyncElasticsearch

from app.core.settings import settings

__all__ = ["create_index", "exists_index", "create_index_if_not_exists"]

INDEX_NAME = "item"

mappings = {
    "properties": {
        "id": {"type": "keyword", "index": True},
        "title": {"type": "keyword", "index": True},
        "description": {"type": "keyword", "index": True},
    },
}


async def create_index(es: AsyncElasticsearch) -> bool:
    await es.indices.create(
        index=INDEX_NAME,
        mappings=mappings,
        settings={
            "index": {
                "number_of_shards": settings.ES.NUMBER_OF_SHARDS,
                "number_of_routing_shards": settings.ES.NUMBER_OF_ROUTING_SHARDS,
                "number_of_replicas": 0,
                "refresh_interval": "30s",
            }
        },
    )
    return True


async def exists_index(es: AsyncElasticsearch) -> bool:
    return bool(await es.indices.exists(index=INDEX_NAME))


async def create_index_if_not_exists(es: AsyncElasticsearch) -> bool:
    if not await exists_index(es):
        return await create_index(es)
    return True
