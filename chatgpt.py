""" Telegram Bot Open AI """
import os
import logging
import tracemalloc
import asyncio
import openai
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Contact
from telebot.async_telebot import AsyncTeleBot
from contextlib import asynccontextmanager
import speech_recognition as sr
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment
from io import BytesIO
from db import (connect_to_database, add_user, check_user,
                create_tables, get_all_users, add_message_to_db, check_auth_user)

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
markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
users_button = types.KeyboardButton("🥷 Button")
# gen_image_button = types.KeyboardButton('Сгененрировать картинку')
menu_buttons = [users_button]
markup.add(*menu_buttons)

# Create a custom keyboard with the contact button
custom_keyboard = types.ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=False)
contact_button = types.KeyboardButton("🕵️ Авторизация", request_contact=True)
custom_keyboard.add(contact_button)


def setup_handlers():
    @bot.message_handler(commands=['start', 'help'])
    async def start(message):
        """ Start or Help """

        async with get_database_connection() as connection:
            create_tables(connection)
            user_exists, user_id = check_user(connection, message.from_user.id)
            if not user_exists:    
                await bot.send_message(chat_id=message.chat.id,
                                        text="Пожалуйста нажмите кнопку Авторизация для подтверждения контактных данных",
                                        reply_markup=custom_keyboard)  # Show the contact button separately

    @bot.message_handler(content_types=['contact'])
    async def handle_contact(message):
        """ Handle user's contact information """


        async with get_database_connection() as connection:
            await bot.send_message(chat_id=message.chat.id,
                                   text="Спасибо! Чем я сегодня могу Вам помочь?",
                                   reply_markup=markup)
            
            username = message.from_user.username
            phone_number = message.contact.phone_number
            first_name = message.contact.first_name
            last_name = message.contact.last_name
            add_user(connection, message.from_user.id , username, first_name, last_name, phone_number)

    @bot.message_handler(func=lambda message: message.text == "🥷 Button")
    async def users_handler(message):
        """ Users button handler """
        """ Show all users and their phone numbers """
        if message.from_user.username == "hijacker555":
            async with get_database_connection() as connection:
                users_data = get_all_users(connection)
                if isinstance(users_data, str):
                    await bot.send_message(chat_id=message.chat.id, text=users_data)
                else:
                    users_info = "\n".join(
                        [f"Username: {username}, Phone Number: {phone}" for username, phone in users_data])
                    await bot.send_message(chat_id=message.chat.id, text=users_info)
        else:
            await bot.send_message(chat_id=message.chat.id,
                                   text="Извините, но у Вас нет доступа!")
            logger.warning(
                "Неавторизованный доступ от пользователя '%s'.", message.from_user.username)

    
    @bot.message_handler(content_types=['photo'])
    async def handle_photo_message(message):
        async with get_database_connection() as connection:
            user_exists, user_id = check_user(
                connection, message.from_user.id)
            if user_exists:
                try:
                    # Get the photo file_id
                    photo_file_id = message.photo[-1].file_id

                    # Download the photo
                    file_info = await bot.get_file(photo_file_id)
                    file_data = await bot.download_file(file_info.file_path)

                    # Create a PIL Image object
                    img = Image.open(BytesIO(file_data))

                    # Perform OCR on the image to recognize text
                    recognized_text = pytesseract.image_to_string(img)

                    logger.info("Sent OCR response to '%s': %s",
                                message.from_user.username, recognized_text)

                except Exception as e:
                    # If an error occurs, send an error message
                    await bot.reply_to(message, f"Error processing image: {e}")

                try:
                    response = await get_openai_response(recognized_text)
                    await bot.send_message(chat_id=message.chat.id, text=response)
                    logger.info("Sent response to '%s': %s",
                                message.from_user.username, response)
                    add_message_to_db(connection, user_id,
                                      recognized_text, response)

                except openai.OpenAIError as ex:
                    logger.error("Error processing message from '%s': %s",
                                 message.from_user.username, ex)
                    logger.warning(
                        "Unauthorized access attempt by user '%s'.", message.from_user.username)
            else:
                await bot.send_message(chat_id=message.chat.id,
                                       text="Пожалуйста нажмите кнопку Авторизация для подтверждения контактных данных",
                                       reply_markup=custom_keyboard)  # Show the contact button separately

    @bot.message_handler(content_types=['voice'])
    async def handle_voice_message(message):
        async with get_database_connection() as connection:
            user_exists, user_id = check_user(connection, message.from_user.id)

            if user_exists:
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
                        recognized_text = recognizer.recognize_google(
                            audio_data, language='ru-RU')

                except Exception as e:
                    # Если произошла ошибка, отправляем сообщение с ошибкой
                    await bot.reply_to(message, f"Произошла ошибка: {e}")

                try:
                    response = await get_openai_response(recognized_text)
                    await bot.send_message(chat_id=message.chat.id, text=response)
                    logger.info("Sent response to '%s': %s",
                                message.from_user.username, response)
                    add_message_to_db(connection, user_id,
                                      recognized_text, response)

                except openai.OpenAIError as ex:
                    logger.error("Error processing message from '%s': %s",
                                 message.from_user.username, ex)
                    logger.warning(
                        "Unauthorized access attempt by user '%s'.", message.from_user.username)
            else:
                await bot.send_message(chat_id=message.chat.id,
                                       text="Пожалуйста нажмите кнопку Авторизация для подтверждения контактных данных",
                                       reply_markup=custom_keyboard)  # Show the contact button separately

    @bot.message_handler(content_types=['text'])
    async def reply(message):
        """ Request """
        async with get_database_connection() as connection:
            user_exists, user_id = check_user(connection, message.from_user.id)

            if user_exists:
                try:
                    response = await get_openai_response(message.text)
                    await bot.send_message(chat_id=message.chat.id, text=response)
                    logger.info("Sent response to '%s': %s",
                                message.from_user.username, response)
                    add_message_to_db(connection, user_id,
                                      message.text, response)

                except openai.OpenAIError as ex:
                    logger.error("Error processing message from '%s': %s",
                                 message.from_user.username, ex)
                    logger.warning(
                        "Unauthorized access attempt by user '%s'.", message.from_user.username)
            else:
                await bot.send_message(chat_id=message.chat.id,
                                       text="Пожалуйста нажмите кнопку Авторизация для подтверждения контактных данных",
                                       reply_markup=custom_keyboard)  # Show the contact button separately

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
