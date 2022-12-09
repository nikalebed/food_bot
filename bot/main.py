import sqlite3
import telebot

import re

bot = telebot.TeleBot("5987759126:AAHL6H-hGHt1EoQMUav_Jz8Eq1CkwPtCH7U")

conn = sqlite3.connect("/Users/evalebedyuk/Desktop/food_data.db", check_same_thread=False)
cursor = conn.cursor()


def db_table_val(user_id: int, user_name: str, likes_dislikes: int, ingredient_name: str):
    cursor.execute('INSERT INTO preferences (user_id, user_name, likes_dislikes, ingredient_name) VALUES (?, ?, ?, ?)',
                   (user_id, user_name, likes_dislikes, ingredient_name))
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

Добавить новый любимый ингредиент: */add_likes ингредиент1, ингредиент2, ...*
Добавить новый НЕ любимый ингредиент: */add_dislikes ингредиент1, ингредиент2, ...*
Убрать любимый ингредиент: */remove_likes ингредиент1, ингредиент2, ...*
Убрать НЕ любимый ингредиент: */remove_dislikes ингредиент1, ингредиент2, ...*

Посмотреть любимое: */my_likes*
Посмотреть НЕ любимое: */my_dislikes*
''', parse_mode="markdown")


def add_ingredient(food: str, pref: int, message):
    pref_to_words = ["нелюбимых", "любимых"]
    query = f'select likes_dislikes from preferences where user_id = \'{message.from_user.id}\' and ingredient_name = \'{food}\''

    previous_pref = cursor.execute(query).fetchone()

    if previous_pref is None:
        db_table_val(user_id=message.from_user.id, user_name=message.from_user.username, likes_dislikes=pref,
                     ingredient_name=food)
        bot.send_message(message.chat.id,
                         f"{food} теперь в вашей базе {pref_to_words[pref]}, @{message.from_user.username}")
    elif previous_pref[0] == pref:
        bot.send_message(message.chat.id,
                         f"{food} уже есть в вашей базе {pref_to_words[pref]}, @{message.from_user.username}")
    else:
        bot.send_message(message.chat.id,
                         f"НЕЛЬЗЯ одновременно и любить, и не любить {food}, @{message.from_user.username}")


def remove_ingredient(food: str, pref: int, message):
    pref_to_words = ["нелюбимых", "любимых"]
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
Введите название ващего любимого ингредиента!
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
Введите название ващего любимого ингредиента!
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
                     f"Любимые ингредиенты @{message.from_user.username}:\n\n" + "\n".join(map(lambda x: x[0], likes)))


@bot.message_handler(commands=['my_dislikes'])
def my_likes(message):
    query = f'select ingredient_name from preferences where user_id =  \'{message.from_user.id} \' and likes_dislikes = 0'
    likes = cursor.execute(query).fetchall()
    bot.send_message(message.chat.id,
                     f"Нелюбимые ингредиенты @{message.from_user.username} 🤢:\n\n" + "\n".join(
                         map(lambda x: x[0], likes)))


bot.polling(none_stop=True)
