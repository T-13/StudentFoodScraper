from models import *

import requests
from bs4 import BeautifulSoup


RESTAURANT_DATA_SOURCE = "https://www.studentska-prehrana.si/sl/restaurant"


def get_restaurant_data():
    """
    Retrieves newest information restaurant data.
    """
    try:
        # Get html from resource
        html = requests.get(RESTAURANT_DATA_SOURCE)
        # Parse html
        document = BeautifulSoup(html.content, 'html.parser')
        # Get restaurant elements
        restaurants = document.find_all(class_="restaurant-row")

        final_data = dict()

        # Retrieve data
        # TODO Thread
        for restaurant in restaurants:
            name = restaurant["data-lokal"]

            # Check if delivery or not
            if "DOSTAVA" not in name:
                if name not in final_data:
                    final_data[name] = restaurant_from_html(restaurant)
                # In case of repetition assume delivery
                else:
                    final_data[name].add_delivery(restaurant)   # Assign delivery
            # If delivery find correct restaurant in dictionary
            else:
                new_name = name[0:-10]
                if new_name in final_data:
                    rest = final_data[new_name]
                    rest.add_delivery(restaurant)   # Assign delivery
                else:
                    new_name = name[0:-9]
                    if new_name in final_data:
                        rest = final_data[new_name]
                        rest.add_delivery(restaurant)   # Assign delivery

        #print("Restaurant data refreshed\nUpdated db with data from: {}\nRestaurants count: {}\nMeal count: {}"
        #      .format(RESTAURANT_DATA_SOURCE, Restaurant.objects.count(), Meal.objects.count()))
        print("Restaurant data from {} refreshed!\nData count: {}"
              .format(RESTAURANT_DATA_SOURCE, len(final_data)))

        #return JsonResponse(response_json(STATUSES["OK"]))
    except Exception as e:
        print("errro: {}".format(e))
        #return JsonResponse(response_json(STATUSES["ERROR_UNKNOWN"]))


get_restaurant_data()
