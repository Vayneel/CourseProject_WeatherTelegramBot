"""
WeatherTelegramBot main module, which consist of message handlers
"""

import telebot  # needed to work with telegram bot
import requests  # needed to request data from openweathermap
import json  # needed to deserialize response from openweathermap

TOKEN = 'YOUR TELEGRAM BOT TOKEN'  # telegram bot token
WEATHER_API = '1a2ccaa70571717574b6617387ea900c'  # openweathermap API
REQUEST_URL_START = 'https://api.openweathermap.org/data/2.5/weather?q='
REQUEST_URL_END = f'&appid={WEATHER_API}&units=metric'
bot = telebot.TeleBot(TOKEN)  # "connecting" to bot
city_message = False  # variable to process messages from user about city, they want to check weather


# you can find bot in telegram by https://t.me/vayneel_weather_bot or @vayneel_weather_bot

@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message) -> None:
    """
    /start command handler
    :param message: Information about user's message
    :return: Nothing
    """
    bot.send_message(message.chat.id, 'Hey! I\'m WeatherForecastBot. To check weather enter /weather')


@bot.message_handler(commands=['weather'])
def weather(message: telebot.types.Message) -> None:
    """
    /weather command handler
    :param message: Information about user's message
    :return: Nothing
    """
    markup = telebot.types.InlineKeyboardMarkup()
    yes_btn = telebot.types.InlineKeyboardButton('Yes!', callback_data='start_yes')  # button
    no_btn = telebot.types.InlineKeyboardButton('No', callback_data='start_no')
    markup.row(yes_btn, no_btn)
    bot.send_message(message.chat.id, 'Hey! Need weather forecast?', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def bot_callback(callback: telebot.types.CallbackQuery) -> None:
    """
    Callback handler
    :param callback: Information about user's call
    :return: Nothing
    """
    global city_message  # using global city message to change it for whole program
    if callback.data == 'start_no':  # processing calls
        bot.edit_message_text('Hey! Need weather forecast?', callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, 'Ok, see you later.')
    elif callback.data == 'start_yes':
        bot.edit_message_text('Hey! Need weather forecast?', callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, 'Enter your city')
        city_message = True  # now next text message from user will be considered as message with name of city


@bot.message_handler(content_types=['text'])
def user_message(message: telebot.types.Message) -> None:
    """
    Text messages handler
    :param message: Information about user's message
    :return: Nothing
    """
    global city_message, REQUEST_URL_START, REQUEST_URL_END
    if city_message:
        city_message = False  # next text message from user won't be considered as message with name of city
        url = REQUEST_URL_START + message.text + REQUEST_URL_END  # creating url from 3 parts
        try:
            result = json.loads(requests.get(url).text)  # converting response into dict type
            # answer string forming
            answer = f'{result["name"]}\n{result["weather"][0]["description"].capitalize()}\n' + \
                     f'Current temperature: {result["main"]["temp"]}\nWind speed: {result["wind"]["speed"]} m/s\n' + \
                     f'Temperature range of today: [{result["main"]["temp_min"]} <=> {result["main"]["temp_max"]}]'
            bot.send_message(message.chat.id, answer)
        except KeyError:
            city_message = True  # next text message from user will be considered as message with name of city
            bot.send_message(message.chat.id, "Seems, you've entered city wrong. Try again")
    else:
        bot.reply_to(message, 'What do you mean by this?? (I can\'t process this query)')


bot.infinity_polling()  # makes program infinite loop
