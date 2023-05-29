""" Telegram Bot Open AI """
import logging
import tracemalloc
import asyncio
import aiohttp
import openai
from telebot import types
from telebot.async_telebot import AsyncTeleBot


tracemalloc.start()


def read_file(file):
    """ Read file """
    with open(file, "r", encoding="UTF-8") as file1:
        for line in file1:
            return line.strip()


# TelegramBot API Endpoint
TOKEN = read_file("telebotapi.txt")
bot = AsyncTeleBot(TOKEN)

# YandexWeather API Endpoint
API_KEY = read_file("yandexweatherapi.txt")
API_URL = 'https://api.weather.yandex.ru/v2/forecast'

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

# Authorized users
AUTHORIZED_USERS = ["hijacker555", "PadreAlexey", "Asmot00"]


@bot.message_handler(commands=['start'])
async def start(message):
    """ Start """
    username = message.from_user.username
    if username in AUTHORIZED_USERS:
        markup = create_menu()
        await bot.send_message(chat_id=message.chat.id,
                               text="Hi, I'm a bot powered by chatGPT. How can I help you today?",
                               reply_markup=markup)
        logger.info("User '%s' authorized and started the bot.", username)
    else:
        await bot.send_message(chat_id=message.chat.id,
                               text="Sorry, you are not authorized to use this bot.")
        logger.warning("Unauthorized access attempt by user '%s'.", username)


@bot.message_handler(func=lambda message: message.text == "chatGPT")
async def openai_handler(message):
    """ chatGPT button handler """
    username = message.from_user.username
    if username in AUTHORIZED_USERS:
        await bot.send_message(chat_id=message.chat.id,
                               text="chatGPT button pressed")
        logger.info("User '%s' pressed chatGPT button", username)
        # Add your OpenAI logic here
    else:
        await bot.send_message(chat_id=message.chat.id,
                               text="Sorry, you are not authorized to use this bot.")
        logger.warning("Unauthorized access attempt by user '%s'.", username)


@bot.message_handler(func=lambda message: message.text == "YandexWeather")
async def openweather_handler(message):
    """ OpenWeather button handler """
    username = message.from_user.username
    if username in AUTHORIZED_USERS:
        await bot.send_message(chat_id=message.chat.id,
                               text="OpenWeather button pressed")
        logger.info("User '%s' pressed OpenWeather button", username)
        await weather_handler(message)
    else:
        await bot.send_message(chat_id=message.chat.id,
                               text="Sorry, you are not authorized to use this bot.")
        logger.warning("Unauthorized access attempt by user '%s'.", username)


async def weather_handler(message):
    """ Weather handler """
    try:
        async with aiohttp.ClientSession() as session:
            headers = {'X-Yandex-API-Key': API_KEY}
            params = {
                'lat': 59.835812,
                'lon': 30.149159,
                'lang': 'ru'
            }
            async with session.get(API_URL, headers=headers, params=params) as response:
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
    if username in AUTHORIZED_USERS:
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
        await bot.send_message(chat_id=message.chat.id,
                               text="Sorry, you are not authorized to use this bot.")
        logger.warning("Unauthorized access attempt by user '%s'.", username)


def create_menu():
    """ Create menu with buttons """
    markup = types.ReplyKeyboardMarkup(row_width=2)
    openai_button = types.KeyboardButton("chatGPT")
    openweather_button = types.KeyboardButton("YandexWeather")
    menu_buttons = [openai_button, openweather_button]
    markup.add(*menu_buttons)
    return markup


if __name__ == '__main__':
    openai.api_key = read_file("openapi.txt")
    logger.info("Bot started")
    asyncio.run(bot.polling())
