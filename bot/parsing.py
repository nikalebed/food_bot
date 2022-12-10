import requests
import json
from requests.structures import CaseInsensitiveDict
from bs4 import BeautifulSoup
from lxml import etree
from urllib.parse import urlencode


def get_recipes(likes, dislikes, dish_type, people_count, prep_time):
    url = ""
    # if dish_type == "breakfast":
    #     url = "https://eda.ru/recepty/zavtraki/ingredienty"
    url = "https://eda.ru/recepty/zavtraki/ingredienty"
    for x in likes:
        url += f"/{x}"
    url += "/eingredienty"
    for x in dislikes:
        url += f"/{x}"

    r = requests.get(url)
    page = r.content.decode("utf-8")
    soup = BeautifulSoup(page, 'html.parser')
    dom = etree.HTML(str(soup))
    ans = {}
    print('search')
    for e in dom.xpath('//div[@class="emotion-m0u77r"]'):
        dish_name = e.xpath('.//span[@class="emotion-1j2opmb"]/text()')[0]
        dish_ref = e.xpath('.//a[@class="emotion-18hxz5k"]/@href')[0]
        portions = int(e.xpath('.//span[@class="emotion-1wl5jqs"]')[0].text)
        time = int(
            e.xpath('.//span[@class="emotion-yelpk7"]')[0].text.split()[0])
        # ans.append({dish_ref: dish_name})

        if portions == people_count and time <= prep_time:
            ans[dish_name] = dish_ref
            if len(ans) == 3:
                break
    print(ans)
    return ans


def get_delivery(query, lat=55.759208, lng=37.643408):
    url = "https://eda.yandex.ru/eats/v1/full-text-search/v1/search"

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    data = {"text": query, "location": {"longitude": lng, "latitude": lat},
            "selector": "all"}
    data = json.dumps(data)
    print(data)
    r = requests.post(url, headers=headers, data=data.encode('utf-8'))
    print(r.status_code)
    page = r.content.decode("utf-8")
    data = json.loads(page)
    ans = []
    for x in data['blocks'][0]['payload']:
        ans.append('https://eda.yandex.ru/r/' + x['brand']['slug'])
    return ans

#print(get_delivery('бейгл'))
# get_delivery("пицца", 55.791046, 37.571103)

# get_recipes([13421, 13747], [15608], "breakfast", 2, 50)
