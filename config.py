""" API keys """
from readfile import read_file


# API Keys
TELEGRAMBOT_API_KEY = read_file("telebotapi.txt")
OPENAI_API_KEY = read_file("openapi.txt")
YANDEX_API_KEY = read_file("yandexweatherapi.txt")


# API Endpoints
YANDEX_API_URL = 'https://api.weather.yandex.ru/v2/forecast'

# DB Config
DB_HOST = "localhost"
DB_DATABASE = "telebot"
DB_USER = "myuser"
DB_PASS = "mypass"
