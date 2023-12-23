import json
import os

from elasticsearch import Elasticsearch
from geopy.geocoders import Nominatim

from index_initiater import IndexInitiator
from reuter import ReutersParser

index_name = "reuters"

es = IndexInitiator(index_name).create()

folder_path = "data"
files_list = os.listdir("data")

# TODO: multiprocess this step
for file in files_list:
    if file.endswith(".sgm"):
        records = ReutersParser().parse(f"{folder_path}/{file}")
        res = es.bulk(index=index_name, operations=records)
        if res["errors"]:
            print(res)
            exit()
        print("code is going well....")
