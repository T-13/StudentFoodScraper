# StudentFoodScraper

Python CLI tool for searching restaurants serving student meals in Slovenia. Supports various filtering to narrow and speed-up the search.

Scrapes https://www.studentska-prehrana.si/ to retrieve data of student restaurants and displays them in nicely formatted text. Scraping code kindly donated by [Leksi](https://leksi.si/) project for wider use.

![Example](https://raw.githubusercontent.com/T-13/StudentFoodScraper/master/example.png)

## Usage

```
usage: studentfood.py [-h] [-m] [-a] [-n NAME] [-c CITY] [-v] [-w]
                      [--wheelchair] [-d] [-l] [-p PRICE]
                      [--price-le PRICE_LE] [--price-ge PRICE_GE] [-o OUT]

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
  --price-le PRICE_LE   require price to be lower than given value
  --price-ge PRICE_GE   require price to be higher than given value
  -o OUT, --out OUT     write to given file (json)
```
