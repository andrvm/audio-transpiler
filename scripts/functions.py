#!/usr/bin/env python
import sqlite3


def init_db() -> None:
    try:
        sqlite_connection = sqlite3.connect('users.db')
        sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS users 
            (id INTEGER PRIMARY KEY, chat_id INTEGER NOT NULL, lang TEXT NOT NULL);
        '''
        cursor = sqlite_connection.cursor()
        cursor.execute(sqlite_create_table_query)
        sqlite_connection.commit()
        cursor.close()
    finally:
        if sqlite_connection:
            sqlite_connection.close()


def register_user(chat_id: int) -> None:
    try:
        sqlite_connection = sqlite3.connect('users.db')
        sqlite_insert_query = f'''INSERT INTO users (chat_id, lang) VALUES ({chat_id}, 'ru-RU');'''
        cursor = sqlite_connection.cursor()
        cursor.execute(sqlite_insert_query)
        sqlite_connection.commit()
        cursor.close()
    except Exception as e:
        print(e)
    finally:
        if sqlite_connection:
            sqlite_connection.close()


def get_user_lang(chat_id: int) -> str:
    try:
        sqlite_connection = sqlite3.connect('users.db')
        sqlite_select_query = f'''SELECT lang FROM users WHERE chat_id = {chat_id} LIMIT 1'''
        cursor = sqlite_connection.cursor()
        cursor.execute(sqlite_select_query)
        row = cursor.fetchone()
        cursor.close()
        default_lang = row[0] if row[0] else 'ru-RU'

    finally:
        if sqlite_connection:
            sqlite_connection.close()

    return default_lang


def check_user(chat_id) -> int:
    try:
        sqlite_connection = sqlite3.connect('users.db')
        sqlite_select_query = f'''SELECT chat_id FROM users WHERE chat_id = {chat_id} LIMIT 1'''
        cursor = sqlite_connection.cursor()
        cursor.execute(sqlite_select_query)
        rows = cursor.fetchall()
        cursor.close()

    finally:
        if sqlite_connection:
            sqlite_connection.close()

    return True if len(rows) else False


def set_user_lang(chat_id: int, lang: str = 'ru-RU') -> bool:
    try:
        sqlite_connection = sqlite3.connect('users.db')
        sqlite_select_query = f'''UPDATE users SET lang = '{lang}' WHERE chat_id = {chat_id}'''
        cursor = sqlite_connection.cursor()
        cursor.execute(sqlite_select_query)
        cursor.close()
        sqlite_connection.commit()
        result = True
    finally:
        if sqlite_connection:
            sqlite_connection.close()

    return result if result else False
