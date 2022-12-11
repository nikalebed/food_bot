def format_dishes(result: dict):
    s = "вот, что я нашел:\n"
    for i, dish_name in enumerate(result.keys()):
        s += f"{i + 1}) <a href='https://eda.ru{result[dish_name]}'>{dish_name}</a> \n"
    return s


def format_deliveries(deliveries):
    s = "здесь можно заказать блюдо:\n"
    for i, res in enumerate(deliveries):
        s += f"{i + 1}:"
        if not res:
            s += f"     не нашлось\n"
            continue
        for ref in res[:5]:
            s += f"     {ref}\n"
    return s


def format_delivery_answer(deliver):
    if deliver == 'no':
        return f"не показывать доставку"
    return ""


def format_add_fav_answer(add_fav):
    if add_fav == "no":
        return f"не добавлять в избранное"
    return f"добавил {int(add_fav) + 1}) в избранное"


def format_dish_type_answer(dish_type):
    return f"ищем {dish_type}"


def format_prep_time_answer(prep_time):
    return f"готовим не больше {prep_time} минут"


def format_people_count_answer(people_count):
    if people_count[1] == people_count[0]:
        return f"порций: {people_count[0]}"
    return f"порций: {people_count[0]} - {people_count[1]}"


def format_is_fav_answer(is_fav):
    if int(is_fav):
        return f"из избранного"
    return f"не из избранного"
