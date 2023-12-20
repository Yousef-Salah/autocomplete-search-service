import json
import os
from typing import Any

import spacy
from bs4 import BeautifulSoup, SoupStrainer
from geopy.geocoders import Nominatim

nlp = spacy.load("en_core_web_lg")
geolocator = Nominatim(user_agent="smart")


class ReutersParser:
    def extract_text(self, element: Any) -> str:
        if element:
            return element.get_text().strip()

        return ""

    def parse(self, file_path) -> list[dict]:
        with open(file_path) as f:
            file_content = f.read()
        soup = BeautifulSoup(file_content, features="html.parser")
        reuters = soup.findAll(str.lower("REUTERS"))
        records = []
        action = {"index": {"_index": "reuters"}}

        counter = 1
        for content in reuters:
            string_converter = lambda x: x.get_text()

            # date = self.extract_text(content.find("date")).replace("'", "").lower()
            topics = list(map(string_converter, content.find("topics").findAll("d")))
            places = list(map(string_converter, content.find("places").findAll("d")))
            people = list(map(string_converter, content.find("people").findAll("d")))
            orgs = list(map(string_converter, content.find("orgs").findAll("d")))
            exchanges = list(
                map(string_converter, content.find("exchanges").findAll("d"))
            )
            companies = list(
                map(string_converter, content.find("companies").findAll("d"))
            )
            title = self.extract_text(content.find("text").find("title"))
            body = self.extract_text(content.find("text").find("body"))
            dateline = self.extract_text(content.find("text").find("dateline"))
            doc = nlp(dateline)
            locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
            location = locations[0] if len(locations) else ""
            longitude = ""
            latitude = ""

            if len(locations):
                location = geolocator.geocode(locations[0])

                if location:
                    longitude = location.longitude
                    latitude = location.latitude

            record = {
                # "date": date,
                "topics": topics,
                "places": places,
                "people": people,
                "orgs": orgs,
                "exchanges": exchanges,
                "companies": companies,
                "title": title,
                "body": body,
                "dateline": dateline,
                "location": {
                    "lat": latitude if latitude != "" else "0",
                    "lon": longitude if longitude != "" else "0",
                },
            }
            records.append(action)
            records.append(record)

            print(f"#f{counter} successfully parsed.")
            counter += 1

        return records
