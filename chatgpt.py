""" Telegram Bot Open AI """
import logging
import openai
import telebot


def readfile(file):
    """ Read file """
    with open(file, "r", encoding="UTF-8") as file1:
        for line in file1:
            return line.strip()


TOKEN = readfile("telebotapi.txt")
bot = telebot.TeleBot(TOKEN)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@bot.message_handler(commands=['start'])
def start(message):
    """ Start """
    bot.send_message(chat_id=message.chat.id,
                     text="Hi, I'm a bot powered by OpenAI. How can I help you today?")


@bot.message_handler(content_types=['text'])
def reply(message):
    """ Request """
    request = message.text
    logger.info("Received message: %s", request)
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
        logger.info("Sent response: %s", response)
    except openai.OpenAIError as ex:
        logger.error("Error processing message: %s", ex)


if __name__ == '__main__':
    openai.api_key = readfile("openapi.txt")
    logger.info("Bot started")
    bot.polling()
