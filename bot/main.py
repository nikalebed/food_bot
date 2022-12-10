import sqlite3
from dataclasses import dataclass, field

import telebot
import re
from markups import get_dish_type_markup, get_prep_time_markup, \
    get_delivery_markup, get_is_fav_markup, get_add_to_fav_markup, \
    get_people_count_markup

import parsing
import formatting

with open("secret.txt") as file:
    lines = [line.rstrip() for line in file]
    TOKEN = lines[0]
    DB_PATH = lines[1]

bot = telebot.TeleBot(TOKEN)
bot.set_my_commands([
    telebot.types.BotCommand("/start", "starts the bot"),
    telebot.types.BotCommand("/help", "shows bot functional"),
    telebot.types.BotCommand("/find_dish", "finds dish"),
    telebot.types.BotCommand("/add_likes", "adds ingrs to likes"),
    telebot.types.BotCommand("/add_dislikes", "adds ingrs to dislikes"),
    telebot.types.BotCommand("/remove_likes", "removes ingrs from likes"),
    telebot.types.BotCommand("/remove_dislikes", "removes ingrs remove dislikes"),
    telebot.types.BotCommand("/my_likes", "shows likes"),
    telebot.types.BotCommand("/my_dislikes", "shows dislikes"),
])

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()


def db_add_preference(user_id: int, user_name: str, likes_dislikes: int, ingredient_name: str, eda_ru_ids: str = None):
    cursor.execute(
        'INSERT INTO preferences (user_id, user_name, likes_dislikes, ingredient_name, eda_ru_ids) VALUES (?, ?, ?, ?, ?)',
        (user_id, user_name, likes_dislikes, ingredient_name, eda_ru_ids))
    conn.commit()


def db_add_favourite(user_id: int, user_name: str, dish_name: str, dish_url: str, dish_type, dish_prep_time,
                     dish_people_count):
    cursor.execute(
        'INSERT INTO favourite_recipes (user_id, user_name, dish_name, dish_url, dish_type, dish_prep_time, dish_people_count) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (user_id, user_name, dish_name, dish_url, dish_type, dish_prep_time, dish_people_count))
    conn.commit()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, '''
🤖 Вас приветствует Бот-Подбиратель-Рецептов! 🤖
    
Познакомьтесь с моим функционалом, нажав */help*
    ''', parse_mode="markdown")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, '''
Функционал бота: */help*

Найти блюдо по вашим предпочтениям: */find_dish*
👇👇👇
Добавить желаемые ингредиенты: */add_likes ингредиент1, ингредиент2, ...*
Добавить нелюбимые ингредиенты: */add_dislikes ингредиент1, ингредиент2, ...*

Убрать ингредиенты из желаемых: */remove_likes ингредиент1, ингредиент2, ...*
Убрать ингредиенты из нелюбимых: */remove_dislikes ингредиент1, ингредиент2, ...*
👇👇👇
Посмотреть желаемое: */my_likes*
Посмотреть нелюбимое: */my_dislikes*
''', parse_mode="markdown")


def get_3_favourites(type, prep_time, people_count):
    query = f'SELECT dish_name, dish_url from favourite_recipes WHERE dish_type = \'{type}\' and dish_prep_time = \'{prep_time}\' and dish_people_count = \'{people_count}\''
    favs = cursor.execute(query).fetchall()[:3]

    favs_dict = {}
    for fav in favs:
        favs_dict[fav[0]] = fav[1]

    return favs_dict


def get_ids(food: str, pref):
    if pref == 0:
        return None

    query = f"SELECT eda_ru_id from eda_ru_ids WHERE ingredient_name LIKE '%{food}%'"

    ids = cursor.execute(query).fetchall()
    if len(ids) == 0:
        return None
    else:
        return " ".join(map(lambda x: str(x[0]), ids))


def add_ingredient(food: str, pref: int, message):
    pref_to_words = ["нелюбимых", "желаемых"]
    query = f'select likes_dislikes from preferences where user_id = \'{message.from_user.id}\' and ingredient_name = \'{food}\''

    previous_pref = cursor.execute(query).fetchone()

    if previous_pref is None:
        db_add_preference(user_id=message.from_user.id, user_name=message.from_user.username, likes_dislikes=pref,
                          ingredient_name=food, eda_ru_ids=get_ids(food, pref))
        bot.send_message(message.chat.id,
                         f"{food} теперь в вашей базе {pref_to_words[pref]}, @{message.from_user.username}")
    elif previous_pref[0] == pref:
        bot.send_message(message.chat.id,
                         f"{food} уже есть в вашей базе {pref_to_words[pref]}, @{message.from_user.username}")
    else:
        bot.send_message(message.chat.id,
                         f"НЕЛЬЗЯ одновременно и любить, и не любить {food}, @{message.from_user.username}")


def remove_ingredient(food: str, pref: int, message):
    pref_to_words = ["нелюбимых", "желаемых"]
    query = f'select id from preferences where user_id = \'{message.from_user.id}\' and ingredient_name = \'{food}\''

    id_to_be_removed = cursor.execute(query).fetchone()

    if id_to_be_removed is None:
        bot.send_message(message.chat.id,
                         f"НЕЛЬЗЯ убрать то, чего нет, @{message.from_user.username}")

    else:
        cursor.execute(f'DELETE FROM preferences WHERE id = \'{id_to_be_removed[0]}\'')
        conn.commit()

        bot.send_message(message.chat.id,
                         f"{food} больше не в вашей базе {pref_to_words[pref]}, @{message.from_user.username}")


@bot.message_handler(commands=['add_likes'])
def add_likes(message):
    s = re.sub(r'\s+', ' ', telebot.util.extract_arguments(message.text))
    likes_to_be_added = set(s.split(sep=","))
    likes_to_be_added.discard(" ")
    likes_to_be_added.discard("")

    if len(likes_to_be_added) == 0:
        bot.send_message(message.chat.id, '''
К сожалению, я не умею читать мысли...
Введите название желаемого ингредиента!
               ''')
        return

    for like in likes_to_be_added:
        add_ingredient(like.strip().lower(), 1, message)


@bot.message_handler(commands=['add_dislikes'])
def add_dislikes(message):
    s = re.sub(r'\s+', ' ', telebot.util.extract_arguments(message.text))
    dislikes_to_be_added = set(s.split(sep=","))
    dislikes_to_be_added.discard(" ")
    dislikes_to_be_added.discard("")

    if len(dislikes_to_be_added) == 0:
        bot.send_message(message.chat.id, '''
К сожалению, я не умею читать мысли...
Введите название ващего нелюбимого ингредиента!
               ''')
        return

    for dislike in dislikes_to_be_added:
        add_ingredient(dislike.strip().lower(), 0, message)


@bot.message_handler(commands=['remove_likes'])
def remove_likes(message):
    s = re.sub(r'\s+', ' ', telebot.util.extract_arguments(message.text))
    likes_to_be_removed = set(s.split(sep=","))
    likes_to_be_removed.discard(" ")
    likes_to_be_removed.discard("")

    if len(likes_to_be_removed) == 0:
        bot.send_message(message.chat.id, '''
К сожалению, я не умею читать мысли...
Введите название желаемого ингредиента!
               ''')
        return

    for like in likes_to_be_removed:
        remove_ingredient(like.strip().lower(), 1, message)


@bot.message_handler(commands=['remove_dislikes'])
def remove_dislikes(message):
    s = re.sub(r'\s+', ' ', telebot.util.extract_arguments(message.text))
    dislikes_to_be_removed = set(s.split(sep=","))
    dislikes_to_be_removed.discard(" ")
    dislikes_to_be_removed.discard("")

    if len(dislikes_to_be_removed) == 0:
        bot.send_message(message.chat.id, '''
К сожалению, я не умею читать мысли...
Введите название ващего нелюбимого ингредиента!
               ''')
        return

    for dislike in dislikes_to_be_removed:
        remove_ingredient(dislike.strip().lower(), 0, message)


@bot.message_handler(commands=['my_likes'])
def my_likes(message):
    query = f'select ingredient_name from preferences where user_id =  \'{message.from_user.id} \' and likes_dislikes = 1'
    likes = cursor.execute(query).fetchall()
    bot.send_message(message.chat.id,
                     f"Желаемые ингредиенты @{message.from_user.username}:\n\n" + "\n".join(map(lambda x: x[0], likes)))


@bot.message_handler(commands=['my_dislikes'])
def my_likes(message):
    query = f'select ingredient_name from preferences where user_id =  \'{message.from_user.id} \' and likes_dislikes = 0'
    likes = cursor.execute(query).fetchall()
    bot.send_message(message.chat.id,
                     f"Нелюбимые ингредиенты @{message.from_user.username} 🤢:\n\n" + "\n".join(
                         map(lambda x: x[0], likes)))


# main function
@dataclass
class DishQuery:
    user_id: int = 0
    dish_names: list = field(default_factory=list)
    dish_urls: list = field(default_factory=list)
    dish_type: str = ""
    dish_prep_time: int = 0
    dish_people_count: list = field(default_factory=list)
    is_fav: bool = False


dish_queries = {}


@bot.message_handler(commands=['find_dish'])
def get_dish(message):
    dish_queries[message.chat.id] = DishQuery()
    dish_queries[message.chat.id].user_id = message.from_user.id
    dish_queries[message.chat.id].user_name = message.from_user.username

    markup = get_dish_type_markup()
    bot.send_message(chat_id=message.chat.id, text="Выберите тип блюда",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('type'))
def answer_dish_type(call):
    dish_type = call.data.split()[1]
    dish_queries[call.message.chat.id].dish_type = dish_type

    bot.edit_message_reply_markup(call.message.chat.id,
                                  call.message.id,
                                  reply_markup=None)
    bot.edit_message_text(formatting.format_dish_type_answer(dish_type),
                          call.message.chat.id,
                          call.message.id)

    markup = get_prep_time_markup()
    bot.send_message(chat_id=call.message.chat.id,
                     text="сколько времени на готовку?",
                     reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('prep_time'))
def answer_prep_type(call):
    prep_time = call.data.split()[1]
    dish_queries[call.message.chat.id].dish_prep_time = int(prep_time)

    bot.edit_message_reply_markup(call.message.chat.id,
                                  call.message.id,
                                  reply_markup=None)
    bot.edit_message_text(formatting.format_prep_time_answer(prep_time),
                          call.message.chat.id,
                          call.message.id)

    markup = get_people_count_markup()
    bot.send_message(chat_id=call.message.chat.id,
                     text="сколько порций?",
                     reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('people_count'))
def answer_people_count(call):
    people_count = [int(call.data.split()[1]), int(call.data.split()[2])]
    dish_queries[call.message.chat.id].dish_people_count = people_count

    bot.edit_message_reply_markup(call.message.chat.id,
                                  call.message.id,
                                  reply_markup=None)

    bot.edit_message_text(formatting.format_people_count_answer(people_count),
                          call.message.chat.id,
                          call.message.id)

    markup = get_is_fav_markup()
    bot.send_message(chat_id=call.message.chat.id,
                     text="выбрать из избранного?",
                     reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('is_fav'))
def answer_is_fav(call):
    is_fav = call.data.split()[1]
    dish_queries[call.message.chat.id].is_fav = int(is_fav)

    bot.edit_message_reply_markup(call.message.chat.id,
                                  call.message.id,
                                  reply_markup=None)
    formatting.format_is_fav_answer(is_fav)
    bot.edit_message_text(formatting.format_is_fav_answer(is_fav),
                          call.message.chat.id,
                          call.message.id)

    result = get_recipes_result(dish_queries[call.message.chat.id])

    if not result:
        bot.send_message(chat_id=call.message.chat.id,
                         text="по вашему запросу ничего не нашлось")
        return

    dish_queries[call.message.chat.id].dish_names = list(result.keys())
    dish_queries[call.message.chat.id].dish_urls = list(result.values())

    bot.send_message(chat_id=call.message.chat.id,
                     text=formatting.format_dishes(result),
                     parse_mode="HTML")
    print("receipt options:", result.keys())

    markup = get_delivery_markup()
    bot.send_message(chat_id=call.message.chat.id,
                     text="посмотреть опции достаки?",
                     reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('deliver'))
def answer_deliver(call):
    deliver = call.data.split()[1]
    bot.edit_message_reply_markup(call.message.chat.id,
                                  call.message.id,
                                  reply_markup=None)
    try:
        bot.edit_message_text(formatting.format_delivery_answer(deliver),
                              call.message.chat.id,
                              call.message.id)
    except:
        bot.delete_message(call.message.chat.id,
                           call.message.id, )
    options = dish_queries[
        call.message.chat.id].dish_names

    if deliver == "yes":
        deliveries = []
        for i, name in enumerate(options):
            result = parsing.get_delivery(name)
            print(result)
            deliveries += [result]

        bot.send_message(chat_id=call.message.chat.id,
                         text=formatting.format_deliveries(deliveries),
                         parse_mode="HTML")

    if not dish_queries[call.message.chat.id].is_fav:
        markup = get_add_to_fav_markup(options)
        bot.send_message(chat_id=call.message.chat.id,
                         text="добавить рецепт в избранное?",
                         reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('add_fav'))
def answer_add_fav(call):
    add_fav = call.data.split()[1]

    bot.edit_message_reply_markup(call.message.chat.id,
                                  call.message.id,
                                  reply_markup=None)
    bot.edit_message_text(formatting.format_add_fav_answer(add_fav),
                          call.message.chat.id,
                          call.message.id)

    if add_fav != "no":
        add_fav = int(add_fav)
        dq = dish_queries[call.message.chat.id]
        db_add_favourite(dq.user_id, dq.user_name, dq.dish_names[add_fav],
                         dq.dish_urls[add_fav],
                         dq.dish_type, dq.dish_prep_time, dq.dish_people_count)


def get_recipes_result(dish_query: DishQuery):
    if dish_query.is_fav:
        return get_3_favourites(dish_query.dish_type,
                                dish_query.dish_prep_time,
                                dish_query.dish_people_count)
    query = f'select ingredient_name from preferences where user_id =  \'{dish_query.user_id} \' and likes_dislikes = 1'
    likes = list(map(lambda x: x[0], cursor.execute(query).fetchall()))

    query = f'select ingredient_name from preferences where user_id =  \'{dish_query.user_id} \' and likes_dislikes = 0'

    dislikes = list(map(lambda x: x[0], cursor.execute(query).fetchall()))
    return parsing.get_recipes(likes, dislikes, dish_query.dish_type,
                               dish_query.dish_people_count,
                               dish_query.dish_prep_time)


# bot.polling(none_stop=True)


bot.polling(none_stop=True)
