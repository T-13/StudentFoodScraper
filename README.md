# StudentFoodScraper

Python CLI tool for searching Slovenian restaurants offering student meals. Supports various filtering to narrow and speed-up the search.

Scrapes https://www.studentska-prehrana.si/ to retrieve data of all restaurants serving student meals in Slovenia and displays them in text.

![Example](https://raw.githubusercontent.com/T-13/StudentFoodScraper/master/example.png)

## Usage

```
usage: studentfood.py [-h] [-m] [-a] [-n NAME] [-c CITY] [-v] [-w]
                      [--wheelchair] [-d] [-l] [-p PRICE]
                      [--price-less PRICE_LESS] [--price-more PRICE_MORE]

Search restaurants providing student food on https://www.studentska-
prehrana.si/

optional arguments:
  -h, --help            show this help message and exit
  -m, --meals           show meals
  -a, --address         show address
  -n NAME, --name NAME  name to search by
  -c CITY, --city CITY  city to search in
  -v, --vegetarian      require vegetarian offer
  -w, --weekends        require weekend offer
  --wheelchair          require wheelchair entrance
  -d, --delivery        require delivery service
  -l, --lunch           require lunch
  -p PRICE, --price PRICE
                        require price to be same as given value
  --price-less PRICE_LESS
                        require price to be lower than given value
  --price-more PRICE_MORE
                        require price to be higher than given value
```
