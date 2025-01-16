from elasticsearch import AsyncElasticsearch

from app.es_models.item import INDEX_NAME
from app.schemas import Item

from .base import BaseESRepository


class ItemESRepository(BaseESRepository):
    async def get_all(self, es: AsyncElasticsearch) -> list[Item]:
        results = await es.search(
            index=self.index_name,
            query={"match_all": {}},
            size=1000,
        )

        return [result["_source"] for result in results["hits"]["hits"]]


item = ItemESRepository(
    index_name=INDEX_NAME,
)
