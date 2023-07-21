""" Telegram Bot Open AI """
import os
import logging
import tracemalloc
import asyncio
import openai
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from contextlib import asynccontextmanager
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from db import (connect_to_database, add_user, check_user,
                create_table, get_all_users)


# Set API keys and other configurations
TELEGRAMBOT_API_KEY = os.environ.get("TELEGRAMBOT_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize the bot
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

# Set up OpenAI API
openai.api_key = OPENAI_API_KEY

# Create menu
markup = types.ReplyKeyboardMarkup(row_width=2)
users_button = types.KeyboardButton("Button")
menu_buttons = [users_button]
markup.add(*menu_buttons)

def setup_handlers():
    @bot.message_handler(commands=['start', 'help'])
    async def start(message):
        """ Start or Help """
        username = message.from_user.username
        connection = connect_to_database()
        if connection:
            # Create database table
            create_table(connection)

            if check_user(connection, username):
                await bot.send_message(chat_id=message.chat.id,
                                       text="Hi, I'm a bot powered by chatGPT. How can I help you today?",
                                       reply_markup=markup)
                logger.info("User '%s' authorized and started the bot.", username)
            else:
                add_user(connection, username)
                await bot.send_message(chat_id=message.chat.id,
                                       text="Hi, I'm a bot powered by chatGPT. How can I help you today?",
                                       reply_markup=markup)
                logger.warning("Unauthorized access attempt by user '%s'.", username)
            connection.close()

    @bot.message_handler(func=lambda message: message.text == "Button")
    async def users_handler(message):
        """ Users button handler """
        username = message.from_user.username
        connection = connect_to_database()
        if connection:
            users_list = get_all_users(connection)
            if username == 'hijacker555':
                await bot.send_message(chat_id=message.chat.id,
                                       text=users_list)
                logger.info("User '%s' pressed Users button", username)
            else:
                await bot.send_message(chat_id=message.chat.id,
                                       text="Sorry, you are not authorized to use this button.")
                logger.warning("Unauthorized access attempt by user '%s'.", username)
            connection.close()

    @bot.message_handler(content_types=['voice'])
    async def handle_voice_message(message):
        async with get_database_connection() as connection:
            if check_user(connection, message.from_user.username):
                logger.info("Received message from '%s': %s", message.from_user.username, message.text)
            else:
                add_user(connection, message.from_user.username)
                logger.info("Received message from '%s': %s", message.from_user.username, message.text)

            try:
                # Получаем аудиофайл как объект bytes
                file_info = await bot.get_file(message.voice.file_id)
                file_data = await bot.download_file(file_info.file_path)

                # Конвертируем аудиофайл в формат WAV
                audio = AudioSegment.from_ogg(BytesIO(file_data))
                wav_data = BytesIO()
                audio.export(wav_data, format="wav")

                # Используем библиотеку SpeechRecognition для распознавания голоса с помощью Google Web Speech API
                recognizer = sr.Recognizer()
                with sr.AudioFile(wav_data) as source:
                    audio_data = recognizer.record(source)
                    recognized_text = recognizer.recognize_google(audio_data, language='ru-RU')

            except Exception as e:
                # Если произошла ошибка, отправляем сообщение с ошибкой
                await bot.reply_to(message, f"Произошла ошибка: {e}")

            try:
                response = await get_openai_response(recognized_text)
                await bot.send_message(chat_id=message.chat.id, text=response)
                logger.info("Sent response to '%s': %s", message.from_user.username, response)

            except openai.OpenAIError as ex:
                logger.error("Error processing message from '%s': %s", message.from_user.username, ex)
                logger.warning("Unauthorized access attempt by user '%s'.", message.from_user.username)

    @bot.message_handler(content_types=['text'])
    async def reply(message):
        """ Request """
        async with get_database_connection() as connection:
            if check_user(connection, message.from_user.username):
                logger.info("Received message from '%s': %s", message.from_user.username, message.text)
            else:
                add_user(connection, message.from_user.username)
                logger.info("Received message from '%s': %s", message.from_user.username, message.text)

            try:
                response = await get_openai_response(message.text)
                await bot.send_message(chat_id=message.chat.id, text=response)
                logger.info("Sent response to '%s': %s", message.from_user.username, response)

            except openai.OpenAIError as ex:
                logger.error("Error processing message from '%s': %s", message.from_user.username, ex)
                logger.warning("Unauthorized access attempt by user '%s'.", message.from_user.username)

    @asynccontextmanager
    async def get_database_connection():
        connection = connect_to_database()
        try:
            yield connection
        finally:
            connection.close()

    async def get_openai_response(request):
        return openai.Completion.create(
            engine="text-davinci-003",
            prompt="You: " + request + "\nBot: ",
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        ).get("choices")[0].text

def main():
    setup_handlers()
    tracemalloc.start()
    logger.info("Bot started")
    asyncio.run(bot.polling())

if __name__ == '__main__':
    main()
