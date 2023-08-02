""" PostgreSQL """
import psycopg2


DB_HOST = "212.86.108.148"
DB_DATABASE = "telebot"
DB_USER = "myuser"
DB_PASS = "mypass"


def connect_to_database():
    """Подключение к базе данных"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_DATABASE,
            user=DB_USER,
            password=DB_PASS
        )
        print("Успешное подключение к базе данных")
        return conn
    except psycopg2.Error as ex:
        print("Ошибка при подключении к базе данных:", ex)
        return None


def create_tables(conn):
    """Создание таблицы authorized_users"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS authorized_users (
        user_id INTEGER PRIMARY KEY,
        username VARCHAR(255) UNIQUE,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        phone_number VARCHAR(20)
    );
    """

    create_messages_table_query = """
    CREATE TABLE IF NOT EXISTS users_messages (
        id SERIAL PRIMARY KEY,
        time TIMESTAMP DEFAULT NOW(),
        user_id INTEGER REFERENCES authorized_users (user_id) ON DELETE CASCADE,
        request TEXT NOT NULL,
        response TEXT NOT NULL
    );
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_table_query)
            cursor.execute(create_messages_table_query)
        conn.commit()
        print("Таблицы 'authorized_users' и 'users_messages' созданы")
    except psycopg2.Error as ex:
        print("Ошибка при создании таблиц:", ex)


def add_user(connection, user_id, username, first_name, last_name, phone):
    # Code to add the user to the 'authorized_users' table
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO authorized_users (user_id, username, first_name, last_name, phone_number) VALUES (%s, %s, %s, %s, %s) RETURNING user_id", (user_id, username, first_name, last_name, phone))
            user_id = cursor.fetchone()[0]
        connection.commit()
        return user_id
    except psycopg2.Error as ex:
        print("Ошибка при добавлении пользователя в базу данных:", ex)


def check_user(connection, user_id):
    """Check if a user exists in the database and return user_id if found"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_id FROM authorized_users WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                # Return a tuple with the boolean and user_phone
                return True, user_data[0]
            else:
                return False, None # Return False and None if user is not found
    except psycopg2.Error as ex:
        print("Ошибка при проверке пользователя в базе данных:", ex)
        return False, None  # Return False and None in case of an error


def check_auth_user(connection, phone):
    """Check if a user exists in the database and return user_id if found"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, phone_number FROM authorized_users WHERE phone_number = %s", (phone,))
            user_data = cursor.fetchone()
            if user_data:
                # Return a tuple with the boolean and user_phone
                return True, user_data[0], user_data[1]
            else:
                return False, None, None  # Return False and None if user is not found
    except psycopg2.Error as ex:
        print("Ошибка при проверке пользователя в базе данных:", ex)
        return False, None, None  # Return False and None in case of an error


def get_all_users(conn):
    """Вывод всех authorized_users из таблицы username"""
    select_query = "SELECT username, phone_number FROM authorized_users;"
    try:
        with conn.cursor() as cursor:
            cursor.execute(select_query)
            results = cursor.fetchall()
            users = [(row[0], row[1] if row[1]
                     is not None else 'None') for row in results]
            return users
    except psycopg2.Error as ex:
        error_message = "Ошибка при получении authorized_users из базы данных: %s", ex
        return error_message


def add_message_to_db(connection, user_id, request, response):
    # Code to add the message to the 'messages' table with a reference to the user in 'authorized_users' table
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users_messages (user_id, request, response) VALUES (%s, %s, %s)", (user_id, request, response))
        connection.commit()
    except psycopg2.Error as ex:
        print("Ошибка при добавлении сообщения в базу данных:", ex)


def update_phone_number(connection, user_id, phone_number):
    """ Update the phone number for an existing user """
    update_query = "UPDATE authorized_users SET phone_number = %s WHERE id = %s;"
    with connection.cursor() as cursor:
        cursor.execute(update_query, (phone_number, user_id))
    connection.commit()
