""" Telegram Bot Open AI """
import openai
import telebot

TOKEN = open("telebotapi.txt", "r").readline
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    """ Start """
    bot.send_message(chat_id=message.chat.id,
                     text="Hi, I'm a bot powered by OpenAI. How can I help you today?")


@bot.message_handler(content_types=['text'])
def reply(message):
    """ Request """
    request = message.text
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt="You: " + request + "\nBot: ",
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    ).get("choices")[0].text
    bot.send_message(chat_id=message.chat.id, text=response)


if __name__ == '__main__':
    openai.api_key = open("openapi.txt", "r").readline
    bot.polling()
