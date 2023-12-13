import json
from typing import Any

import spacy
from bs4 import BeautifulSoup, SoupStrainer
from geopy.geocoders import Nominatim

"""
    REUTERS:
        Date:
        TOPICS: multi topic listed in which each one is surronded by <D>
        PLACES: multi place liste in which each place is surrounded by <D>

"""
nlp = spacy.load("en_core_web_lg")

f = open("data/reut2-000.sgm", "r")
data = f.read()
soup = BeautifulSoup(data, features="html.parser")
contents = soup.findAll(str.lower("REUTERS"))
geolocator = Nominatim(user_agent="smart")


def extract_text(element: Any) -> str:
    if element:
        return element.get_text().strip()

    return ""


records = []
counter = 1
for content in contents:
    string_converter = lambda x: x.get_text()

    date = extract_text(content.find("date"))
    topics = list(map(string_converter, content.find("topics").findAll("d")))
    places = list(map(string_converter, content.find("places").findAll("d")))
    people = list(map(string_converter, content.find("people").findAll("d")))
    orgs = list(map(string_converter, content.find("orgs").findAll("d")))
    exchanges = list(map(string_converter, content.find("exchanges").findAll("d")))
    companies = list(map(string_converter, content.find("companies").findAll("d")))
    title = extract_text(content.find("text").find("title"))
    body = extract_text(content.find("text").find("body"))
    dateline = extract_text(content.find("text").find("dateline"))
    doc = nlp(dateline)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    location = locations[0] if len(locations) else ""
    longitude = ""
    latitude = ""

    if len(locations):
        location = geolocator.geocode(locations[0])

        if location:
            longitude = location.latitude
            latitude = location.longitude

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
        "longitude": longitude,
        "latitude": latitude,
    }

    records.append(record)
    print(counter)
    counter += 1

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(records, f)
