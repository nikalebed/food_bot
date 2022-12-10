from lxml import etree
from bs4 import BeautifulSoup
import requests
import sqlite3

with open("secret.txt") as file:
    lines = [line.rstrip() for line in file]
    DB_PATH = lines[1]

conn0 = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor0 = conn0.cursor()


def db_ingredient(eda_ru_id: int, ingredient_name: str):
    cursor0.execute(
        'INSERT INTO eda_ru_ids (eda_ru_id, ingredient_name) VALUES (?, ?)',
        (eda_ru_id, ingredient_name))
    conn0.commit()


# categories = ["alkogol", "bakaleya", "gotovye-produkty", "griby", "zelen-travy", "krupy-bobovye-muka",
#               "molochnye-produkty-yayca", "myaso-myasnaya-gastronomiya", "ovoschi-korneplody", "orehi", "ptica",
#               "ryba-moreprodukty", "specii-pripravy", "syry", "frukty-yagody"]

# хотим базу ид : ингредиент
# добавлять сразу все ломает сайт, так что надо по кускам

# categories = ["alkogol", "bakaleya", "gotovye-produkty", "griby", "zelen-travy", "krupy-bobovye-muka",
#               "molochnye-produkty-yayca"]

categories = ["myaso-myasnaya-gastronomiya", "ovoschi-korneplody", "orehi", "ptica", "ryba-moreprodukty",
              "specii-pripravy", "syry", "frukty-yagody"]

for category in categories:
    pg = 1
    print(category)

    url = f"https://eda.ru/wiki/ingredienty/{category}?page={pg}"
    r = requests.get(url)
    page = r.content.decode("utf-8")
    soup = BeautifulSoup(page, 'html.parser')

    dom = etree.HTML(str(soup))
    hrefs = dom.xpath('//div[@class="emotion-wxopay"]//a[not(@class="emotion-m0lpw0")]/@href')
    ingredients = dom.xpath('//div[@class="emotion-wxopay"]//a[not(@class="emotion-m0lpw0")]//text()')

    while len(hrefs) > 0:
        for i in range(len(hrefs)):
            db_ingredient(int(hrefs[i].split(sep='-')[-1]), ingredients[i].lower())

        pg += 1

        url = f"https://eda.ru/wiki/ingredienty/{category}?page={pg}"
        r = requests.get(url)
        page = r.content.decode("utf-8")

        soup = BeautifulSoup(page, 'html.parser')

        dom = etree.HTML(str(soup))
        hrefs = dom.xpath('//div[@class="emotion-wxopay"]//a[not(@class="emotion-m0lpw0")]/@href')
        ingredients = dom.xpath('//div[@class="emotion-wxopay"]//a[not(@class="emotion-m0lpw0")]//text()')





