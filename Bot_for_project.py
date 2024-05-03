
import sys
import json
import telebot
import requests
from currency_converter import CurrencyConverter
from telebot import types
from Bot_for_project_token import token

bot = telebot.TeleBot("6733305516:AAHng-m5dXVj2v6WRK3o7D36vLtrkClrPxE")
API = "467f3620a8af34c95a0abb353ff4f996"

currency = CurrencyConverter()
amount = 0
keyboard = telebot.types.ReplyKeyboardMarkup(True)
keyboard.row("Мой профиль", "Погода", "Конвертор валют", "Новости", "Поддержка", "Закончить работу")


# ======================== Commands

@bot.message_handler(commands=["start"])
def answer(message):
    bot.send_message(message.chat.id,"Здравствуйте, вот что я могу:")
    bot.send_message(message.chat.id, "/weather - узнать погоду в городе.")
    bot.send_message(message.chat.id, "/convert - конвертор валют.")
    bot.send_message(message.chat.id, "/calculator - калькулятор")


@bot.message_handler(commands=["weather"])
def weather(message):
    bot.send_message(message.chat.id, "Напишите название города:")


@bot.message_handler(commands=["convert"])
def conv(message):
    bot.send_message(message.chat.id, "Введите сумму:")
    bot.register_next_step_handler(message, summa)


@bot.message_handler(commands=['stop'])
def stop_bot(message):
    bot.send_message(message.chat.id, "Бот остановлен.")
    bot.stop_polling()


@bot.message_handler(commands=["calculator"])
def calc_eval(message):
    bot.send_message(message.chat.id, "Введите выражение:")
    bot.register_next_step_handler(message, calculate)



def send(id, text):
    bot.send_message(id, text, reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def get_weather(message):
    gorod = message.text.strip().lower()
    try:
        res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={gorod}&appid={API}&units=metric")
        data = json.loads(res.text)
        temp = data["main"]["temp"]
        bot.reply_to(message, f"Сейчас погода в городе {gorod.title()}: +{int(temp)} \N{DEGREE SIGN}C")
    except Exception:
        bot.send_message(message.chat.id, "Такого города не существует")
    return


def summa(message):
    global amount
    try:
        amount = float(message.text.strip())
    except Exception:
        bot.send_message(message.chat.id, "Неверный формат. Попробуйте начать заново.")
        bot.register_next_step_handler(message, summa)
        return
    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("USD/EUR", callback_data="usd/eur")
        btn2 = types.InlineKeyboardButton("EUR/USD", callback_data="eur/usd")
        btn3 = types.InlineKeyboardButton("Другое значение", callback_data="else")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, "Выберите пару валют", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Число должно быть больше 0. Введите сумму")
        bot.register_next_step_handler(message, summa)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data != "else":
        values = call.data.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(call.message.chat.id, f"{amount} {values[0]} = {round(res, 2)} {values[1]}.")
        bot.register_next_step_handler(call.message, summa)
    else:
        bot.send_message(call.message.chat.id, "Введите пару значений через /")
        bot.register_next_step_handler(call.message, my_currency)
    return


def my_currency(message):
    try:
        values = message.text.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f"Получается: {round(res, 2)}.")
        bot.register_next_step_handler(message, summa)
    except Exception:
        bot.send_message(message.chat.id, "Что-то не так. Впишите значение заново")
        bot.register_next_step_handler(message, my_currency)
    return

def calculate(message):
    expression = message.text.strip()
    try:
        result = eval(expression)
        bot.send_message(message.chat.id, f"Результат: {result}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")
    return


if __name__ == '__main__':
    bot.polling()
