import requests
from bs4 import BeautifulSoup


class Restaurant():
    name = ""
    longitude = 0.0
    latitude = 0.0
    address = ""
    price = 0.0
    payment = 0.0
    city = ""

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

    def __str__(self):
        return self.city + ": " + self.name

    def to_json(self):
        return model_to_json(Restaurant, self)

    def add_delivery(self, delivery):
        self.delivery = True
        self.delivery_price = float(delivery["data-cena"].replace(",", "."))
        self.delivery_payment = float(delivery["data-doplacilo"].replace(",", "."))


class Meal():
    main_meal = ""
    extras = ""
    restaurant = None  # class Restaurant

    def __str__(self):
        return self.main_meal

    def to_json(self):
        return model_to_json(Meal, self, serialize_related=False)


def restaurant_from_html(element):
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

    # Define menu for restaurant
    menu_from_html(element["data-detailslink"], restaurant)

    return restaurant


def menu_from_html(source, restaurant):
    # If no source don't bother
    if not source:
        return
    if len(source.strip()) <= 0:
        return

    url = "https://www.studentska-prehrana.si/{}".format(source)
    # Get html from resource
    html = requests.get(url)
    # Parse html
    document = BeautifulSoup(html.content, 'html.parser')
    # Get restaurant elements
    menu_entries = document.find(id="menu-list")
    for entry in menu_entries.find_all(class_="shadow-wrapper"):
        try:
            meal_from_html(entry, restaurant)
        except Exception as e:
            pass
            #print("{} in {} has no menu.\nResult of: {}"
            #      .format(restaurant.name, restaurant.city, e))


def meal_from_html(element, restaurant):
    meal = Meal()
    meal.restaurant = restaurant
    temp = element.find_all("p")[0].find_all("h5")[0]

    # Get main meal
    meal.main_meal = temp.find_all("strong")[0].get_text()

    extras = ""
    # Retrieve extras
    for extra in element.find_all("ul")[0].find_all("li"):
        extra_food = extra.find_all("i")[0].get_text()
        if extra_food:
            if len(extra_food) > 0 and "&nbsp" not in extra_food:
                extras += extra_food.strip() + ";"

    meal.extras = extras
