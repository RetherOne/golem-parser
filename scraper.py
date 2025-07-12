from csv import DictWriter
from os import getenv

from dotenv import load_dotenv
from requests import get

# Loading environment variables
load_dotenv()
url = "https://api.golemio.cz/v2/municipallibraries"
api = getenv("API_KEY")


# Function for formatting library working hours
def format_opening_hours(hours_list: list) -> str:
    days = []
    for entry in hours_list:
        if entry.get("is_default"):
            day = entry["day_of_week"][:3]
            opens = entry.get("opens", "//")
            closes = entry.get("closes", "//")
            days.append(f"{day} {opens}-{closes}")
    return "; ".join(days)


# Collecting data from Golemio API
def collect_data(url: str, api_key: str) -> list[dict]:
    headers = {"Accept": "application/json", "X-Access-Token": api_key}

    request = get(url, headers=headers)
    data = request.json()["features"]
    result = []
    for lib in data:
        geo_lib = lib["geometry"]
        prop_lib = lib["properties"]
        temp_dict = {}

        temp_dict["id"] = prop_lib["id"]
        temp_dict["name"] = prop_lib["name"]
        temp_dict["street"] = prop_lib["address"]["street_address"]
        temp_dict["postal_code"] = prop_lib["address"]["postal_code"]
        temp_dict["city"] = prop_lib["address"]["address_locality"]
        temp_dict["region"] = prop_lib["district"].capitalize()
        temp_dict["country"] = prop_lib["address"]["address_country"]
        temp_dict["latitude"] = geo_lib["coordinates"][1]
        temp_dict["longitude"] = geo_lib["coordinates"][0]
        temp_dict["opening_hours"] = format_opening_hours(prop_lib["opening_hours"])
        result.append(temp_dict)
    return result


# Saving to a CSV file
def save_to_csv(data: list[dict], filename: str) -> None:
    fieldnames = [
        "id",
        "name",
        "street",
        "postal_code",
        "city",
        "region",
        "country",
        "latitude",
        "longitude",
        "opening_hours",
    ]

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


if __name__ == "__main__":
    filename = "libraries.csv"

    collect = collect_data(url=url, api_key=api)
    save_to_csv(collect, filename)

    print(f'All available data was written in a file: "{filename}"')
