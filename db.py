""" PostgreSQL """
import psycopg2
from config import (DB_HOST, DB_DATABASE,
                    DB_USER, DB_PASS)


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


def create_table(conn):
    """Создание таблицы authorized_users"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS authorized_users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE
    );
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_table_query)
        conn.commit()
        print("Таблица authorized_users создана")
    except psycopg2.Error as ex:
        print("Ошибка при создании таблицы authorized_users:", ex)


def add_user(conn, username):
    """Добавление пользователя в базу данных"""
    insert_query = "INSERT INTO authorized_users (username) VALUES (%s);"
    try:
        with conn.cursor() as cursor:
            cursor.execute(insert_query, (username,))
        conn.commit()
        print(
            f"Пользователь {username} добавлен в базу данных")
    except psycopg2.Error as ex:
        print("Ошибка при добавлении пользователя в базу данных:", ex)


def check_user(conn, username):
    """Проверка наличия пользователя в базе данных"""
    select_query = "SELECT EXISTS(SELECT 1 FROM authorized_users WHERE username = %s);"
    try:
        with conn.cursor() as cursor:
            cursor.execute(select_query, (username,))
            result = cursor.fetchone()[0]
            if result:
                return True
            else:
                return False
    except psycopg2.Error as ex:
        print("Ошибка при проверке наличия пользователя в базе данных:", ex)
