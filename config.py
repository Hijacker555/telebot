""" API keys """
from readfile import read_file

# Authorized users
AUTHORIZED_USERS = ["hijacker555", "PadreAlexey", "Asmot00"]

# API Keys
TELEGRAMBOT_API_KEY = read_file("telebotapi.txt")
OPENAI_API_KEY = read_file("openapi.txt")
YANDEX_API_KEY = read_file("yandexweatherapi.txt")


# API Endpoints
YANDEX_API_URL = 'https://api.weather.yandex.ru/v2/forecast'
