from typing import Mapping

from elasticsearch import Elasticsearch, client


class IndexInitiator:
    def __init__(
        self, index_name: str, api_link: str = "http://localhost:9200"
    ) -> None:
        self.__index_name = index_name
        self.__api_link = api_link

    def create(self) -> Elasticsearch:
        es = Elasticsearch(hosts=[self.__api_link])

        if es.indices.exists(index=self.__index_name):
            es.indices.delete(index=self.__index_name)

        es.indices.create(
            index=self.__index_name, mappings=self.__configurations()["mappings"]
        )
        print("index created")
        return es

    def __configurations(self):
        return {
            "settings": self.__get_settings(),
            "mappings": self.__get_mappings(),
        }

    def __get_settings(self):
        return {
            "number_of_shards": "1",
        }

    def __get_mappings(self):
        return {
            "properties": {
                # "date": {"type": "date", "format": "dd-MMM-yyyy HH:mm:ss.SS"},
                "topics": {
                    "type": "keyword",
                    "ignore_above": 256,
                },
                "places": {
                    "type": "keyword",
                    "ignore_above": 256,
                },
                "people": {
                    "type": "keyword",
                    "ignore_above": 256,
                },
                "orgs": {
                    "type": "keyword",
                    "ignore_above": 256,
                },
                "exchanges": {
                    "type": "keyword",
                    "ignore_above": 256,
                },
                "companies": {
                    "type": "keyword",
                    "ignore_above": 256,
                },
                "title": {
                    "type": "keyword",
                    "ignore_above": 256,
                },
                "content": {
                    "type": "text",
                    "analyzer": "standard",
                },
                "location": {
                    "type": "geo_point",
                },
            }
        }
