import requests
import json
from requests.structures import CaseInsensitiveDict


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
    for x in data['blocks'][0]['payload']:
        print('https://eda.yandex.ru/r/' + x['brand']['slug'])


get_delivery("бейгл")
get_delivery("пицца",55.791046, 37.571103)
