import telebot

TOKEN = "5634876039:AAHxC1Tu0qbIkiMJOuSTrQPx599xPXh4UWQ"

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Heloo ")

bot.polling(none_stop=True)