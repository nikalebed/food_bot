import telebot
from telebot import types


def get_dish_type_markup():
    markup_dish_type = types.InlineKeyboardMarkup()
    breakfast = types.InlineKeyboardButton(text="завтрак",
                                           callback_data="type breakfast")
    lunch = types.InlineKeyboardButton(text="обед", callback_data="type lunch")
    dinner = types.InlineKeyboardButton(text="ужин",
                                        callback_data="type dinner")
    snack = types.InlineKeyboardButton(text="перекус",
                                       callback_data="type snack")
    dessert = types.InlineKeyboardButton(text="десерт",
                                         callback_data="type dessert")

    markup_dish_type.add(breakfast, lunch, dinner, snack, dessert)
    return markup_dish_type


def get_prep_time_markup():
    markup_prep_time = types.InlineKeyboardMarkup()
    b1 = types.InlineKeyboardButton(text="1 -15 мин",
                                    callback_data="prep_time 15")
    b2 = types.InlineKeyboardButton(text="15 - 45 мин",
                                    callback_data="prep_time 45")
    b3 = types.InlineKeyboardButton(text="45мин - 1,5часа",
                                    callback_data="prep_time 90")
    b4 = types.InlineKeyboardButton(text="45мин - 1,5часа",
                                    callback_data="prep_time 1000")
    markup_prep_time.add(b1, b2, b3, b4)
    return markup_prep_time


def get_people_count_markup():
    markup_people_count = types.InlineKeyboardMarkup()
    b1 = types.InlineKeyboardButton(text="1",
                                    callback_data="people_count 1 1")
    b2 = types.InlineKeyboardButton(text="2",
                                    callback_data="people_count 2 2")
    b3 = types.InlineKeyboardButton(text="3-4",
                                    callback_data="people_count 3 4")
    b4 = types.InlineKeyboardButton(text="5+",
                                    callback_data="people_count 5 100")
    markup_people_count.add(b1, b2, b3, b4)
    return markup_people_count


def get_is_fav_markup():
    markup = types.InlineKeyboardMarkup()
    b1 = types.InlineKeyboardButton(text="да",
                                    callback_data="is_fav 1")
    b2 = types.InlineKeyboardButton(text="нет",
                                    callback_data="is_fav 0")
    markup.add(b1, b2)
    return markup


def get_delivery_markup():
    markup = types.InlineKeyboardMarkup()
    b1 = types.InlineKeyboardButton(text="да",
                                    callback_data=f"deliver yes")
    b2 = types.InlineKeyboardButton(text="нет",
                                    callback_data=f"deliver no")
    markup.add(b1, b2)
    return markup


def get_add_to_fav_markup(options):
    markup = types.InlineKeyboardMarkup()
    for i in range(len(options)):
        b = types.InlineKeyboardButton(text=f"рецепт {i + 1}",
                                       callback_data=f"add_fav {i}")
        markup.add(b)
    b = types.InlineKeyboardButton(text="нет",
                                   callback_data=f"add_fav no")
    markup.add(b)
    return markup
