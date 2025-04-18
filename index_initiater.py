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
            index=self.__index_name,
            settings=self.__configurations()["settings"],
            mappings=self.__configurations()["mappings"],
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
            "number_of_shards": 2,
            "number_of_replicas": 1,
            "index": {
                "max_ngram_diff": 7,
            },
            "analysis": {
                "filter": {
                    "ngram_filter": {
                        "type": "ngram",
                        "min_gram": 3,
                        "max_gram": 10,
                    },
                    "my_custom_stop_words_filter": {
                        "type": "stop",
                        "ignore_case": True,
                        "stopwords": ["the", "and", "is"],
                    },
                    "less_than_3_filter": {
                        "type": "length",
                        "min": 3,
                    },
                    "english_stemmer": {
                        "type": "stemmer",
                        "language": "english",
                    },
                },
                "analyzer": {
                    "title_processing": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "char_filter": ["html_strip"],
                        "filter": [
                            "lowercase",
                            "ngram_filter",
                            "my_custom_stop_words_filter",
                            "less_than_3_filter",
                        ],
                    },
                    "text_processing": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "char_filter": ["html_strip"],
                        "filter": [
                            "lowercase",
                            "my_custom_stop_words_filter",
                            "less_than_3_filter",
                            "english_stemmer",
                        ],
                    },
                },
            },
        }

    def __get_mappings(self):
        return {
            "properties": {
                "date": {
                    "type": "date",
                    "format": "dd-MMM-yyyy HH:mm:ss",
                },
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
                "author": {
                    "type": "nested",
                    "properties": {
                        "first_name": {"type": "keyword"},
                        "last_name": {"type": "keyword"},
                    },
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
                    "type": "text",
                    "analyzer": "title_processing",
                },
                # TODO: make sure to get rid of tags elements
                "content": {
                    "type": "text",
                    "analyzer": "text_processing",
                },
                "place": {
                    "type": "keyword",
                    "ignore_above": 256,
                },
                "location": {
                    "type": "geo_point",
                },
                "temporal_expressions": {
                    "type": "keyword",
                    "ignore_above": 256,
                },
                "georeferences": {
                    "type": "geo_point",
                },
                "georeferences_string": {
                    "type": "keyword",
                },
            }
        }
