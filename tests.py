""" Unit tests """
import unittest
from unittest.mock import patch, MagicMock
from chatgpt import (start, users_handler, openweather_handler, reply,
                     add_db_table, weather_handler)


class TestBot(unittest.TestCase):
    """ TestBot """

    def setUp(self):
        self.bot = MagicMock()

    @patch('your_module.connect_to_database')
    def test_start_authorized_user(self, mock_connect_to_database):
        """ Test start authorized users """
        mock_connection = MagicMock()
        mock_connect_to_database.return_value = mock_connection
        mock_check_user = MagicMock(return_value=True)
        mock_add_user = MagicMock()
        mock_create_menu = MagicMock(return_value='mock_menu')
        mock_send_message = MagicMock()
        self.bot.send_message = mock_send_message

        with patch('your_module.check_user', mock_check_user), \
                patch('your_module.add_user', mock_add_user), \
                patch('your_module.create_menu', mock_create_menu):

            start(self.bot.message)

        mock_connect_to_database.assert_called_once()
        mock_check_user.assert_called_once_with(
            mock_connection, self.bot.message.from_user.username)
        mock_create_menu.assert_called_once()
        mock_send_message.assert_called_once_with(chat_id=self.bot.message.chat.id,
                        text="Hi, I'm a bot powered by chatGPT. How can I help you today?",
                        reply_markup='mock_menu')
        self.assertFalse(mock_add_user.called)
        mock_connection.close.assert_called_once()

    @patch('your_module.connect_to_database')
    def test_start_unauthorized_user(self, mock_connect_to_database):
        """ Test strat unauthirized users """
        mock_connection = MagicMock()
        mock_connect_to_database.return_value = mock_connection
        mock_check_user = MagicMock(return_value=False)
        mock_add_user = MagicMock()
        mock_create_menu = MagicMock(return_value='mock_menu')
        mock_send_message = MagicMock()
        self.bot.send_message = mock_send_message

        with patch('your_module.check_user', mock_check_user), \
                patch('your_module.add_user', mock_add_user), \
                patch('your_module.create_menu', mock_create_menu):

            start(self.bot.message)

        mock_connect_to_database.assert_called_once()
        mock_check_user.assert_called_once_with(
            mock_connection, self.bot.message.from_user.username)
        mock_create_menu.assert_called_once()
        mock_send_message.assert_called_once_with(chat_id=self.bot.message.chat.id,
                            text="Hi, I'm a bot powered by chatGPT. How can I help you today?",
                            reply_markup='mock_menu')
        mock_add_user.assert_called_once_with(
            mock_connection, self.bot.message.from_user.username)
        mock_connection.close.assert_called_once()

    @patch('your_module.connect_to_database')
    def test_users_handler_authorized_user(self, mock_connect_to_database):
        """ Test users handler authorized user """
        mock_connection = MagicMock()
        mock_connect_to_database.return_value = mock_connection
        mock_get_all_users = MagicMock(return_value='mock_users')
        mock_send_message = MagicMock()
        self.bot.send_message = mock_send_message
        self.bot.message.text = 'Button'
        self.bot.message.from_user.username = 'hijacker555'

        with patch('your_module.get_all_users', mock_get_all_users):

            users_handler(self.bot.message)

        mock_connect_to_database.assert_called_once()
        mock_get_all_users.assert_called_once_with(mock_connection)
        mock_send_message.assert_called_once_with(chat_id=self.bot.message.chat.id,
                                                  text='mock_users')
        mock_connection.close.assert_called_once()

    @patch('your_module.connect_to_database')
    def test_users_handler_unauthorized_user(self, mock_connect_to_database):
        """ Test users handler unauthorized user """
        mock_connection = MagicMock()
        mock_connect_to_database.return_value = mock_connection
        mock_get_all_users = MagicMock()
        mock_send_message = MagicMock()
        self.bot.send_message = mock_send_message
        self.bot.message.text = 'Button'
        self.bot.message.from_user.username = 'unauthorized_user'

        with patch('your_module.get_all_users', mock_get_all_users):

            users_handler(self.bot.message)

        mock_connect_to_database.assert_called_once()
        self.assertFalse(mock_get_all_users.called)
        mock_send_message.assert_called_once_with(chat_id=self.bot.message.chat.id,
                                text="Sorry, you are not authorized to use this button.")
        mock_connection.close.assert_called_once()


@patch('your_module.connect_to_database')
def test_openweather_handler_authorized_user(self, mock_connect_to_database):
    """ Test openweather handler authorized user """
    mock_connection = MagicMock()
    mock_connect_to_database.return_value = mock_connection
    mock_check_user = MagicMock(return_value=True)
    mock_send_message = MagicMock()
    self.bot.send_message = mock_send_message
    self.bot.message.text = 'YandexWeather'
    self.bot.message.from_user.username = 'authorized_user'

    with patch('your_module.check_user', mock_check_user), \
            patch('your_module.add_user') as mock_add_user:

        openweather_handler(self.bot.message)

    mock_connect_to_database.assert_called_once()
    mock_check_user.assert_called_once_with(
        mock_connection, self.bot.message.from_user.username)
    mock_send_message.assert_called_once_with(chat_id=self.bot.message.chat.id,
                                              text="OpenWeather button pressed")
    self.assertFalse(mock_add_user.called)
    mock_connection.close.assert_called_once()

    @patch('your_module.connect_to_database')
    def test_openweather_handler_unauthorized_user(self, mock_connect_to_database):
        mock_connection = MagicMock()
        mock_connect_to_database.return_value = mock_connection
        mock_check_user = MagicMock(return_value=False)
        mock_add_user = MagicMock()
        mock_send_message = MagicMock()
        self.bot.send_message = mock_send_message
        self.bot.message.text = 'YandexWeather'
        self.bot.message.from_user.username = 'unauthorized_user'

        with patch('your_module.check_user', mock_check_user), \
                patch('your_module.add_user', mock_add_user):

            openweather_handler(self.bot.message)

        mock_connect_to_database.assert_called_once()
        mock_check_user.assert_called_once_with(
            mock_connection, self.bot.message.from_user.username)
        mock_send_message.assert_called_once_with(chat_id=self.bot.message.chat.id,
                                                  text="OpenWeather button pressed")
        mock_add_user.assert_called_once_with(
            mock_connection, self.bot.message.from_user.username)
        mock_connection.close.assert_called_once()


@patch('your_module.aiohttp.ClientSession')
@patch('your_module.connect_to_database')
async def test_weather_handler_success(self, mock_connect_to_database, mock_client_session):
    """ Test weather handler succes """
    mock_connection = MagicMock()
    mock_connect_to_database.return_value = mock_connection
    mock_send_message = MagicMock()
    self.bot.reply_to = mock_send_message
    self.bot.message.chat.id = 'mock_chat_id'

    mock_json_data = {
        'fact': {
            'temp': 25,
            'condition': 'Sunny'
        }
    }

    mock_get = mock_client_session.return_value.get
    mock_get.return_value.__aenter__.return_value.json.return_value = mock_json_data

    with patch('your_module.aiohttp.ClientSession.get') as mock_get:
        await weather_handler(self.bot.message)

    mock_connect_to_database.assert_called_once()
    mock_get.assert_called_once_with(
        'mock_yandex_api_url',
        headers={'X-Yandex-API-Key': 'mock_yandex_api_key'},
        params={
            'lat': 59.835812,
            'lon': 30.149159,
            'lang': 'ru'
        }
    )
    mock_send_message.assert_called_once_with(
        self.bot.message, 'Temperature: 25°C\n Sunny')
    mock_connection.close.assert_called_once()


@patch('your_module.aiohttp.ClientSession')
@patch('your_module.connect_to_database')
async def test_weather_handler_no_data(self, mock_connect_to_database, mock_client_session):
    """ Test weather handler no data """
    mock_connection = MagicMock()
    mock_connect_to_database.return_value = mock_connection
    mock_send_message = MagicMock()
    self.bot.reply_to = mock_send_message
    self.bot.message.chat.id = 'mock_chat_id'

    mock_json_data = {}

    mock_get = mock_client_session.return_value.get
    mock_get.return_value.__aenter__.return_value.json.return_value = mock_json_data

    with patch('your_module.aiohttp.ClientSession.get', mock_get):
        await weather_handler(self.bot.message)

    mock_connect_to_database.assert_called_once()
    mock_get.assert_called_once_with(
        'mock_yandex_api_url',
        headers={'X-Yandex-API-Key': 'mock_yandex_api_key'},
        params={
            'lat': 59.835812,
            'lon': 30.149159,
            'lang': 'ru'
        }
    )
    self.assertFalse(mock_send_message.called)
    mock_connection.close.assert_called_once()

    @patch('your_module.openai.Completion.create')
    @patch('your_module.connect_to_database')
    async def test_reply_unauthorized_user(self, mock_connect_to_database, mock_create_completion):
        mock_connection = MagicMock()
        mock_connect_to_database.return_value = mock_connection
        mock_check_user = MagicMock(return_value=False)
        mock_add_user = MagicMock()
        mock_send_message = MagicMock()
        self.bot.send_message = mock_send_message
        self.bot.message.text = 'mock_request'
        self.bot.message.from_user.username = 'unauthorized_user'

        mock_create_completion.return_value.get.return_value.text = 'mock_response'

        with patch('your_module.check_user', mock_check_user), \
                patch('your_module.add_user', mock_add_user):

            await reply(self.bot.message)

        mock_connect_to_database.assert_called_once()
        mock_check_user.assert_called_once_with(
            mock_connection, self.bot.message.from_user.username)
        mock_create_completion.assert_called_once_with(
            engine="text-davinci-003",
            prompt="You: mock_request\nBot: ",
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        mock_send_message.assert_called_once_with(chat_id=self.bot.message.chat.id,
                                                  text='mock_response')
        mock_add_user.assert_called_once_with(
            mock_connection, self.bot.message.from_user.username)
        mock_connection.close.assert_called_once()

    @patch('your_module.connect_to_database')
    def test_add_db_table(mock_connect_to_database):
        mock_connection = MagicMock()
        mock_connect_to_database.return_value = mock_connection
        mock_execute = MagicMock()
        mock_connection.execute = mock_execute

        add_db_table()

        mock_connect_to_database.assert_called_once()
        mock_execute.assert_called_once_with(
            '''CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE
            )'''
        )
        mock_connection.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
