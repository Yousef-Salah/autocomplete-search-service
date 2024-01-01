import json
import os
import re
from functools import reduce
from time import sleep
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
        # TODO: Refactor code
        with open(file_path) as f:
            file_content = f.read()
        soup = BeautifulSoup(file_content, features="html.parser")
        reuters = soup.findAll(str.lower("REUTERS"))
        records = []
        action = {"index": {"_index": "reuters"}}

        counter = 1
        for content in reuters:
            string_converter = lambda x: x.get_text()

            whole_rueter_text = content.get_text()

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
                dateline, title, whole_rueter_text
            )
            temporal_expressions = self.__get_temporal_expressions(whole_rueter_text)
            georeferences = self.__get_georeferences(whole_rueter_text)
            author = self.__process_author(content.find("author"))

            record = {
                "date": date,
                "topics": topics,
                "places": places,
                "people": people,
                "author": author,
                "orgs": orgs,
                "exchanges": exchanges,
                "companies": companies,
                "title": title,
                "content": body,
                "dateline": dateline,
                "place": location,
                "location": {
                    "lat": latitude if latitude != "" else "0",
                    "lon": longitude if longitude != "" else "0",
                },
                "temporal_expressions": temporal_expressions,
                "georeferences": georeferences,
                "georeferences_string": list(map(lambda x: str(x), georeferences)),
            }

            records.append(action)
            records.append(record)

            print(f"#f{counter} successfully parsed.")
            counter += 1

        return records

    def __get_location_details(
        self, dateline: str, title: str, whole_rueter_text: str
    ) -> Tuple[str, float, float]:
        texts = [dateline, title]

        for text in texts:
            text_location_details = self.__extract_geocode_from_text(text)

            if text_location_details:
                return text_location_details

        return self.__estimate_geolocation(whole_rueter_text)

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

    def __get_temporal_expressions(self, whole_rueter_text: str) -> list[str]:
        result = nlp(whole_rueter_text)

        temporal_expressions = [ent.text for ent in result.ents if ent.label_ == "DATE"]

        return temporal_expressions

    def __get_georeferences(self, whole_rueter_text) -> list[Tuple[float, float]]:
        locations = self.__extract_locations(whole_rueter_text)

        georeferences = list(map(lambda x: self.__extract_geocode(x), locations))
        return [geocode for geocode in georeferences if geocode != False]

    def __estimate_geolocation(
        self, whole_rueter_text: str
    ) -> Tuple[str, float, float]:
        georeferences = self.__get_georeferences(whole_rueter_text)
        number_of_georeferences = len(georeferences)
        if number_of_georeferences:
            summmed_georeferences = reduce(
                lambda x, y: (x[0] + y[0], x[1] + y[1]), georeferences
            )

            return (
                # TODO: Get location from geo_point
                "IDK",
                summmed_georeferences[0] / number_of_georeferences,
                summmed_georeferences[1] / number_of_georeferences,
            )
        else:
            return "Null Island", 0, 0

    def __process_author(self, author_text_element) -> dict:
        if author_text_element:
            author_name: str = author_text_element.get_text()

            if author_name:
                author_name = author_name.strip()
                terms = author_name.split(" ")
                first_name: str = terms[1]
                last_name: str = terms[2].replace(",", "")

            return {
                "first_name": first_name,
                "last_name": last_name,
            }

        return {
            "first_name": "",
            "last_name": "",
        }
