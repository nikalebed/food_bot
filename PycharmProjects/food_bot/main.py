import sqlite3
import telebot
from ast import arguments

bot = telebot.TeleBot("5987759126:AAHL6H-hGHt1EoQMUav_Jz8Eq1CkwPtCH7U")

conn = sqlite3.connect('/Users/evalebedyuk/Desktop/food_bot_database.db', check_same_thread=False)
cursor = conn.cursor()


def db_table_val(user_id: int, user_name: str, likes_dislikes: int, food_name: str):
    cursor.execute('INSERT INTO preferences (user_id, user_name, likes_dislikes, food_name) VALUES (?, ?, ?, ?)',
                   (user_id, user_name, likes_dislikes, food_name))
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
Добавить новый любимый ингредиент: */add_likes ингредиент*
Добавить новый НЕ любимый ингредиент: */add_dislikes ингредиент*
Убрать любимый ингредиент: */remove_likes ингредиент*
Убрать НЕ любимый ингредиент: */remove_dislikes ингредиент*

🤖🤖🤖 
Прошу заметить, что при добавлении/удалении нескольких ингредиентов сразу */update_dislikes кефир молоко)*
Происходит то же самое, что и при */update_dislikes сгущеное молоко*

(держу в курсе)
🤖🤖🤖 
''', parse_mode="markdown")



@bot.message_handler(commands=['add_likes'])
def add_likes(message):
    new_like = telebot.util.extract_arguments(message.text)

    if len(new_like) == 0:
        bot.send_message(message.chat.id, '''
К сожалению, я не умею читать мысли...
Введите название ващего любимого ингредиента!
        ''')
        return

    db_table_val(user_id=message.from_user.id, user_name=message.from_user.username, likes_dislikes=1,
                 food_name=new_like)
    bot.send_message(message.chat.id, f"{new_like.strip()} теперь в вашей базе, @{message.from_user.username}")

@bot.message_handler(commands=['my_likes'])
def add_likes(message):

bot.polling(none_stop=True)