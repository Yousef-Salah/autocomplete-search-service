from elasticsearch import Elasticsearch


class IndexInitiator:
    def __init__(self, index_name: str) -> None:
        self.__index_name = index_name

    def create(self):
        es = Elasticsearch()

        if es.indices.exists(self.__index_name):
            es.indices.delete(self.__index_name)

        es.indices.create(
            index=self.__index_name, ignore=400, body=self.__configurations
        )

    def __configurations(self):
        return {"settings": self.__get_settings(), "mappings": self.__get_mappings()}

    def __get_settings(self):
        return {
            "analysis": {
                "filter": {
                    "ngram_filter": {"type": "ngram", "min_gram": 3, "max_gram": 4}
                },
                "analyzer": {
                    "text_processing": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "ngram_filter"],
                    }
                },
            }
        }

    def __get_mappings(self):
        return {
            "properties": {
                "date": {
                    "type": "date",
                },
                "topics": {
                    "type": "keyword",
                    "ignore": 256,
                },
                "places": {
                    "type": "keyword",
                    "ignore": 256,
                },
                "people": {
                    "type": "keywrod",
                    "ignore": 256,
                },
                "orgs": {
                    "type": "keywrod",
                    "ignore": 256,
                },
                "exchanges": {
                    "type": "keywrod",
                    "ignore": 256,
                },
                "companies": {
                    "type": "keywrod",
                    "ignore": 256,
                },
                "title": {
                    "type": "keyword",
                    "ignore": 256,
                },
                "body": {"type": "keyword", "ignore": 256},
                "latitude": {
                    "type": "double",
                },
                "longitude": {
                    "type": "double",
                },
                "latitude": {
                    "type": "double",
                },
            }
        }


# {
#     "date": "3-MAR-1987 04:40:42.53",
#     "topics": [],
#     "places": ["uk"],
#     "people": [],
#     "orgs": [],
#     "exchanges": [],
#     "companies": [],
#     "title": "MERRILL MANDATED FOR IEL U.S. NOTE.",
#     "body": "",
#     "dateline": "LONDON, March 3 -",
#     "longitude": 51.5074456,
#     "latitude": -0.1277653
#   },
