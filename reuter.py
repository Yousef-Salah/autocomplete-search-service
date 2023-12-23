import json
import os
import re
from typing import Any, Tuple

import spacy
from bs4 import BeautifulSoup, SoupStrainer
from geopy.geocoders import Nominatim
from unidecode import unidecode

nlp = spacy.load("en_core_web_lg")
geolocator = Nominatim(user_agent="smart")


class ReutersParser:
    def __extract_text(self, element: Any) -> str:
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
            if counter == 10:
                return records
            string_converter = lambda x: x.get_text()

            date = self.__precess_date(content.find("date"))
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
            title = self.__extract_text(content.find("text").find("title"))
            body = self.__extract_text(content.find("text").find("body"))
            dateline = self.__extract_text(content.find("text").find("dateline"))
            location, longitude, latitude = self.__get_location_details(
                dateline, title, body
            )

            if location == None:
                print((location, longitude, latitude))

                exit()

            record = {
                "date": date,
                "topics": topics,
                "places": places,
                "people": people,
                "orgs": orgs,
                "exchanges": exchanges,
                "companies": companies,
                "title": title,
                "body": body,
                "dateline": dateline,
                "place": location,
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

    def __get_location_details(
        self, dateline: str, title: str, body: str
    ) -> Tuple[str, float, float]:
        # try to get locations from dateline
        texts = [dateline, title, body]

        for text in texts:
            text_location_details = self.__extract_geocode_from_text(text)

            if text_location_details:
                return text_location_details

        return "Null Island", 0, 0

    def __extract_locations(self, text: str) -> list:
        text = str(text)
        processed_text = nlp(text.lower())
        return [ent.text for ent in processed_text.ents if ent.label_ == "GPE"]

    def __extract_geocode(self, location: str) -> Tuple[float, float] | bool:
        geocodes = geolocator.geocode(location)

        if geocodes:
            return geocodes.longitude, geocodes.latitude

        return False

    def __extract_geocode_from_text(self, text: str) -> Tuple[str, float, float] | bool:
        text_locations = self.__extract_locations(text)
        text_geocodes = list(
            map(lambda x: (x, self.__extract_geocode(x)), text_locations)
        )
        filtered_text_geocodes = list(filter(lambda x: x[1] != False, text_geocodes))

        if len(filtered_text_geocodes):
            location, gecodes = filtered_text_geocodes[0]
            return location, gecodes[0], gecodes[1]
        return False

    def __precess_date(self, date: Any) -> str:
        valid_date_length = 20
        text = self.__extract_text(date)
        text = text.strip()
        text: str = unidecode(text)
        text = re.sub(r"\..*$", "", text)

        if len(text) != valid_date_length:
            text = "0" + text

        text = text[:4] + str.lower(text[4]) + str.lower(text[5]) + text[6:]
        return re.sub(r"\..*$", "", text)
