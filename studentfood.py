#!/usr/bin/env python3

import sys

import requests
from bs4 import BeautifulSoup
import progressbar as pb


BASE_URL = "https://www.studentska-prehrana.si/"
RESTAURANT_EXT = "sl/restaurant"


class Restaurant():
    name = ""
    longitude = 0.0
    latitude = 0.0
    address = ""
    price = 0.0
    payment = 0.0
    city = ""
    meals = []

    # Has vegetarian meals
    vegi = False
    # Is open on weekends
    weekends = False
    # Has entry for wheelchair
    for_disabled = False
    # Has delivery
    delivery = False
    delivery_price = 0.0
    delivery_payment = 0.0

    @classmethod
    def from_html(self, element):
        # Retrieve restaurant data from tags
        restaurant = Restaurant()
        try:
            restaurant.latitude = float(element["data-lon"].replace(",", "."))
            restaurant.longitude = float(element["data-lat"].replace(",", "."))
        except ValueError:
            pass

        restaurant.address = element["data-naslov"]
        restaurant.price = float(element["data-cena"].replace(",", "."))
        restaurant.payment = float(element["data-doplacilo"].replace(",", "."))
        restaurant.name = element["data-lokal"]
        restaurant.city = element["data-city"]

        # Check for extra info using icons and their tooltips
        extras = element.find_all("img")
        for extra in extras:
            if extra["title"] == "Vegetarijansko":
                restaurant.vegi = True
            elif extra["title"] == "Dostop za invalide":
                restaurant.for_disabled = True
            elif extra["title"] == "Odprt ob vikendih":
                restaurant.weekends = True

        return restaurant

    def __repr__(self):
        text = "{} ({})\n".format(self.name, self.city)
        for meal in self.meals:
            text += "- {}\n".format(meal)
        return text

    def to_json(self):
        return model_to_json(Restaurant, self)

    def add_delivery(self, delivery):
        self.delivery = True
        self.delivery_price = float(delivery["data-cena"].replace(",", "."))
        self.delivery_payment = float(delivery["data-doplacilo"].replace(",", "."))


class Meal():
    main_meal = ""
    extras = ""

    def __repr__(self):
        return "{} ({})".format(self.main_meal, self.extras)

    @classmethod
    def from_html(self, element):
        meal = Meal()
        temp = element.find_all("p")[0].find_all("h5")[0]

        # Get main meal (split by spaces to get rid of leading number)
        meal.main_meal = temp.find_all("strong")[0].get_text().split("  ")[1]

        # Retrieve extras
        extras = element.find_all("ul")[0].find_all("li")
        for extra in extras:
            extra_food = extra.find_all("i")[0].get_text()
            if extra_food:
                if len(extra_food) > 0 and "&nbsp" not in extra_food:
                    if meal.extras != "":
                        meal.extras += ", "
                    meal.extras += extra_food.strip()

        return meal

    def to_json(self):
        return model_to_json(Meal, self, serialize_related=False)


def main():
    try:
        # Get html from resource, parse it and get all restaurant elements
        html = requests.get("{}/{}".format(BASE_URL, RESTAURANT_EXT))
        document = BeautifulSoup(html.content, 'html.parser')
        restaurants = document.find_all(class_="restaurant-row")

        found = []

        # Retrieve data
        print("Searching restaurants on {}...".format(BASE_URL))
        for element in pb.progressbar(restaurants[:2]):
            # Parse restaurant basic data
            restaurant = Restaurant.from_html(element)

            # Parse restaurant details - ignore if no details provided
            source = element["data-detailslink"]
            if not source or len(source.strip()) <= 0:
                continue

            # Get html from resource and parse it
            url = "{}/{}".format(BASE_URL, source)
            html = requests.get(url)
            document = BeautifulSoup(html.content, 'html.parser')

            # Get meal elements
            meals = document.find(id="menu-list")
            for entry in meals.find_all(class_="shadow-wrapper"):
                try:
                    restaurant.meals.append(Meal.from_html(entry))
                except Exception as e:
                    pass  # No menu/meal defined

            found.append(restaurant)

        print()
        for f in found:
            print(f)

        print("Found {} restaurants!".format(len(found)))

    except Exception as e:
        print("Failed to fetch restaurants! {}".format(e))
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
