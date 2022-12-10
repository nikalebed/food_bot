def format_dishes(result: dict):
    s = "вот, что я нашел:\n"
    for i, dish_name in enumerate(result.keys()):
        s += f"{i + 1}) <a href='https://eda.ru/recepty{result[dish_name]}'>{dish_name}</a> \n"
    return s


def format_deliveries(result):
    s = "ваше блюдо нашлось в:\n"
    for i, res in enumerate(result[:5]):
        s += f"{i + 1}) {res}\n"
    return s
