#!/usr/bin/env python3

import sys
import argparse

import requests
from bs4 import BeautifulSoup
import progressbar as pb
from termcolor import colored


BASE_URL = "https://www.studentska-prehrana.si/"
RESTAURANT_EXT = "sl/restaurant"


class Restaurant():
    name = ""
    longitude = 0.0
    latitude = 0.0
    address = ""
    price_student = 0.0
    price_full = 0.0
    city = ""
    meals = []

    vegi = False
    weekends = False
    for_disabled = False
    delivery = False
    lunch = False

    @classmethod
    def from_html(cls, element):
        # Retrieve restaurant data from tags
        restaurant = cls()

        try:
            restaurant.latitude = float(element["data-lon"].replace(",", "."))
            restaurant.longitude = float(element["data-lat"].replace(",", "."))
        except ValueError:
            pass

        restaurant.address = element["data-naslov"]
        try:
            restaurant.price_full = float(element["data-cena"].replace(",", "."))
            restaurant.price_student = float(element["data-doplacilo"].replace(",", "."))
        except ValueError:
            pass
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
            elif extra["title"] == "Dostava":
                restaurant.delivery = True
            elif extra["title"] == "Kosilo":
                restaurant.lunch = True

        return restaurant

    def __repr__(self):
        text = "{} {}".format(colored(self.name, attrs=["bold", "underline"]),
                              colored("({})".format(self.city), attrs=["dark"]))

        if self.vegi:         text += colored(" [VEGGIE]", "yellow")
        if self.weekends:     text += colored(" [WEEKEND]", "yellow")
        if self.for_disabled: text += colored(" [WHEELCHAIR]", "yellow")
        if self.delivery:     text += colored(" [DELIVERY]", "yellow")
        if self.lunch:        text += colored(" [LUNCH]", "yellow")

        text += " => {} {}".format(colored("{}€".format(self.price_student), attrs=["bold"]),
                                   colored("({}€)".format(self.price_full), attrs=["dark"]))

        for meal in self.meals:
            text += "\n- {}".format(meal)

        return text


class Meal():
    main_meal = ""
    extras = ""

    def __repr__(self):
        return "{} {}".format(self.main_meal,
                              colored("({})".format(self.extras), attrs=["dark"]))

    @classmethod
    def from_html(cls, element):
        meal = cls()
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


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Search restaurants providing student food on {}".format(BASE_URL))
    parser.add_argument("-m", "--meals", action="store_true", help="show meals")
    parser.add_argument("-a", "--address", action="store_true", help="show address")
    parser.add_argument("-n", "--name", type=str, default="", help="name to search by")
    parser.add_argument("-c", "--city", type=str, default="", help="city to search in")
    parser.add_argument("-v", "--vegetarian", action="store_true", help="require vegetarian offer")
    parser.add_argument("-w", "--weekends", action="store_true", help="require weekend offer")
    parser.add_argument("--wheelchair", action="store_true", help="require wheelchair entrance")
    parser.add_argument("-d", "--delivery", action="store_true", help="require delivery service")
    parser.add_argument("-l", "--lunch", action="store_true", help="require lunch")
    parser.add_argument("-p", "--price", type=float, default=-1.0, help="require price to be same as given value")
    parser.add_argument("--price-le", type=float, default=float("inf"), help="require price to be lower than given value")
    parser.add_argument("--price-ge", type=float, default=0.0, help="require price to be higher than given value")

    args = parser.parse_args();
    args.name = args.name.lower().strip()
    args.city = args.city.lower().strip()

    # Search
    try:
        # Get html from resource, parse it and get all restaurant elements
        html = requests.get("{}/{}".format(BASE_URL, RESTAURANT_EXT))
        document = BeautifulSoup(html.content, 'html.parser')
        restaurants = document.find_all(class_="restaurant-row")

        found = []

        # Retrieve data
        print("Searching restaurants on {}...".format(BASE_URL))
        for element in pb.progressbar(restaurants):
            # Parse restaurant basic data
            restaurant = Restaurant.from_html(element)

            # Conditions
            if args.name and args.name not in restaurant.name.lower().strip(): continue
            if args.city and args.city not in restaurant.city.lower().strip(): continue
            if args.vegetarian and not restaurant.vegi:         continue
            if args.weekends and not restaurant.weekends:       continue
            if args.wheelchair and not restaurant.for_disabled: continue
            if args.delivery and not restaurant.delivery:       continue
            if args.lunch and not restaurant.lunch:             continue
            if args.price >= 0.0 and args.price != restaurant.price_student: continue
            if restaurant.price_student > args.price_le:                     continue
            if restaurant.price_student < args.price_ge:                     continue


            found.append(restaurant)

            # Parse restaurant details - ignore if no details provided
            if not args.meals:
                continue

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

        # Pretty print
        if not args.meals:
            print()

        for f in found:
            if args.meals:
                print()

            print(f)
            if args.address:
                print(colored("[{} ({}, {})]".format(f.address, f.longitude, f.latitude), attrs=["dark"]))


        print("\nFound {} restaurants!".format(len(found)))

    except Exception as e:
        print("Failed to fetch restaurants! {}".format(e))
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
