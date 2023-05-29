""" Telegram Bot Open AI """
import logging
import openai
import telebot


def read_file(file):
    """ Read file """
    with open(file, "r", encoding="UTF-8") as file1:
        for line in file1:
            return line.strip()


TOKEN = read_file("telebotapi.txt")
bot = telebot.TeleBot(TOKEN)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create file handler for logging
file_handler = logging.FileHandler('/var/log/bot.log')
file_handler.setLevel(logging.INFO)

# Create formatter and add it to the file handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)

# Authorized users
AUTHORIZED_USERS = ["hijacker555", "user2", "user3"]

@bot.message_handler(commands=['start'])
def start(message):
    """ Start """
    username = message.from_user.username
    if username in AUTHORIZED_USERS:
        bot.send_message(chat_id=message.chat.id,
                         text="Hi, I'm a bot powered by OpenAI. How can I help you today?")
        logger.info("User '%s' authorized and started the bot.", username)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Sorry, you are not authorized to use this bot.")
        logger.warning("Unauthorized access attempt by user '%s'.", username)


@bot.message_handler(content_types=['text'])
def reply(message):
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

            bot.send_message(chat_id=message.chat.id, text=response)
            logger.info("Sent response to '%s': %s", username, response)
        except openai.OpenAIError as ex:
            logger.error("Error processing message from '%s': %s", username, ex)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Sorry, you are not authorized to use this bot.")
        logger.warning("Unauthorized access attempt by user '%s'.", username)


if __name__ == '__main__':
    openai.api_key = read_file("openapi.txt")
    logger.info("Bot started")
    bot.polling()
