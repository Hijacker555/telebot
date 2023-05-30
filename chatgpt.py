""" Telegram Bot Open AI """
import logging
import tracemalloc
import asyncio
import aiohttp
import openai
from config import (TELEGRAMBOT_API_KEY, YANDEX_API_KEY,
                    YANDEX_API_URL, OPENAI_API_KEY)
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from db import (connect_to_database, add_user, check_user,
                create_table, get_all_users)


bot = AsyncTeleBot(TELEGRAMBOT_API_KEY)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create file handler for logging
file_handler = logging.FileHandler('bot.log')
file_handler.setLevel(logging.INFO)

# Create formatter and add it to the file handler
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)


@bot.message_handler(commands=['start'])
async def start(message):
    """ Start """
    username = message.from_user.username
    connection = connect_to_database()
    if connection:
        create_table(connection)
        if check_user(connection, username):
            markup = create_menu()
            await bot.send_message(chat_id=message.chat.id,
                                text="Hi, I'm a bot powered by chatGPT. How can I help you today?",
                                   reply_markup=markup)
            logger.info("User '%s' authorized and started the bot.", username)
        else:
            add_user(connection, username)
            markup = create_menu()
            await bot.send_message(chat_id=message.chat.id,
                                text="Hi, I'm a bot powered by chatGPT. How can I help you today?",
                                   reply_markup=markup)
            logger.warning(
                "Unauthorized access attempt by user '%s'.", username)
        connection.close()


@bot.message_handler(func=lambda message: message.text == "Button")
async def users_handler(message):
    """ Users button handler """
    username = message.from_user.username
    connection = connect_to_database()
    if connection:
        create_table(connection)
        if username == 'hijacker555':
            await bot.send_message(chat_id=message.chat.id,
                                   text=get_all_users(connection))
            logger.info("User '%s' pressed Users button", username)
        else:
            await bot.send_message(chat_id=message.chat.id,
                                   text="Sorry, you are not authorized to use this button.")
            logger.warning(
                "Unauthorized access attempt by user '%s'.", username)
        connection.close()


@bot.message_handler(func=lambda message: message.text == "YandexWeather")
async def openweather_handler(message):
    """ OpenWeather button handler """
    username = message.from_user.username
    connection = connect_to_database()
    if connection:
        create_table(connection)
        if check_user(connection, username):
            await bot.send_message(chat_id=message.chat.id,
                                   text="OpenWeather button pressed")
            logger.info("User '%s' pressed OpenWeather button", username)
            await weather_handler(message)
        else:
            add_user(connection, username)
            await bot.send_message(chat_id=message.chat.id,
                                   text="OpenWeather button pressed")
            logger.warning(
                "Unauthorized access attempt by user '%s'.", username)
        connection.close()


async def weather_handler(message):
    """ Weather handler """
    try:
        async with aiohttp.ClientSession() as session:
            headers = {'X-Yandex-API-Key': YANDEX_API_KEY}
            params = {
                'lat': 59.835812,
                'lon': 30.149159,
                'lang': 'ru'
            }
            async with session.get(YANDEX_API_URL, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    fact = data.get('fact')
                    if fact:
                        temperature = fact.get('temp')
                        weather_description = fact.get('condition')
                        weather_info = f"Temperature: {temperature}°C\n {weather_description}"
                        await bot.reply_to(message, weather_info)
                        logger.info(
                            "Weather information sent to user: %s", weather_info)
                    else:
                        logger.warning(
                            "No weather information found in the API response")
                else:
                    logger.error(
                        "Failed to retrieve weather information. Status code: %d", response.status)
    except aiohttp.ClientError as ex:
        logger.error(
            "An error occurred while processing the message: %s", str(ex))


@bot.message_handler(content_types=['text'])
async def reply(message):
    """ Request """
    username = message.from_user.username
    connection = connect_to_database()
    if connection:
        create_table(connection)
        if check_user(connection, username):
            request = message.text
            logger.info("Received message from '%s': %s", username, request)
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt="You: " + request + "\nBot: ",
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    temperature=0.5,
                ).get("choices")[0].text

                await bot.send_message(chat_id=message.chat.id, text=response)
                logger.info("Sent response to '%s': %s", username, response)
            except openai.OpenAIError as ex:
                logger.error(
                    "Error processing message from '%s': %s", username, ex)
        else:
            add_user(connection, username)
            request = message.text
            logger.info("Received message from '%s': %s", username, request)
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt="You: " + request + "\nBot: ",
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    temperature=0.5,
                ).get("choices")[0].text

                await bot.send_message(chat_id=message.chat.id, text=response)
                logger.info("Sent response to '%s': %s", username, response)
            except openai.OpenAIError as ex:
                logger.error(
                    "Error processing message from '%s': %s", username, ex)
            logger.warning(
                "Unauthorized access attempt by user '%s'.", username)
        connection.close()


def create_menu():
    """ Create menu with buttons """
    markup = types.ReplyKeyboardMarkup(row_width=2)
    users_button = types.KeyboardButton("Button")
    openweather_button = types.KeyboardButton("YandexWeather")
    menu_buttons = [users_button, openweather_button]
    markup.add(*menu_buttons)
    return markup


if __name__ == '__main__':
    tracemalloc.start()
    openai.api_key = OPENAI_API_KEY
    logger.info("Bot started")
    asyncio.run(bot.polling())
