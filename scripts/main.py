#!/usr/bin/env python
import logging
import os
import uuid
import telebot
from telebot import types
import speech_recognition as sr
from pydub import AudioSegment
from dotenv import load_dotenv
from telebot import apihelper

from functions import (
    init_db,
    check_user,
    register_user,
    get_user_lang,
    set_user_lang
)

"""
    Initialization
"""
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.environ.get("APP_TOKEN")
bot = telebot.TeleBot(TOKEN)
apihelper.API_URL = "http://89.124.109.228:9099/bot{0}/{1}"
apihelper.FILE_URL = "http://89.124.109.228:9099/file/bot{0}/{1}"
init_db()
logger.info("Bot initialized successfully")


@bot.message_handler(content_types=["audio", "voice"])
def handle_voice(message):
    chat_id = message.chat.id
    wav_file = None
    ogg_file = None

    try:
        user_lang = get_user_lang(chat_id=chat_id)
        user_lang_mark = "🇷🇺" if user_lang == "ru-RU" else "🇬🇧"
        logger.info("Processing audio from chat_id=%s, lang=%s", chat_id, user_lang)

        bot.send_message(chat_id, f"Начинаем обработку, перекодируем на {user_lang_mark} ...\n")

        unique_name = uuid.uuid4()
        wav_file = f"{unique_name}.wav"
        ogg_file = f"{unique_name}.ogg"

        if message.content_type == "audio":
            file_info = bot.get_file(message.audio.file_id)
        else:
            file_info = bot.get_file(message.voice.file_id)

        downloaded_file = bot.download_file(file_info.file_path)
        with open(ogg_file, "wb") as new_file:
            new_file.write(downloaded_file)
        logger.debug("Audio saved to %s", ogg_file)

        sound = AudioSegment.from_file(ogg_file)
        sound.export(wav_file, format="wav")
        logger.debug("Transcoded to WAV: %s", wav_file)

        r = sr.Recognizer()
        with sr.AudioFile(wav_file) as source:
            audio = r.record(source)
            out = r.recognize_google(audio, language=user_lang)

        logger.info("Recognition result for chat_id=%s: %s", chat_id, out)

        os.remove(wav_file)
        os.remove(ogg_file)
        logger.debug("Cleaned up temp files")

    except Exception as e:
        logger.exception("Error processing audio for chat_id=%s: %s", chat_id, e)
        if wav_file and os.path.exists(wav_file):
            os.remove(wav_file)
        if ogg_file and os.path.exists(ogg_file):
            os.remove(ogg_file)
        out = "Извините, но что-то пошло не так...\n\r"
        out += f"Возможно вы выбрали неправильный язык перекодировки, текущий - {user_lang_mark}. Выбор языка доступен в /settings."

    finally:
        bot.reply_to(message, out)


@bot.message_handler(
    content_types=[c for c in ["text", "document", "sticker", "photo", "video"] if c not in ["audio", "voice"]]
)
def handle_data(message):
    lang_ru = types.InlineKeyboardButton("🇷🇺 Русский", callback_data="ru")
    lang_en = types.InlineKeyboardButton("🇬🇧 Английский", callback_data="en")

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(lang_ru)
    keyboard.add(lang_en)

    chat_id = message.chat.id
    logger.info("Text message from chat_id=%s: %s", chat_id, message.text)

    if not check_user(chat_id):
        register_user(chat_id)
        logger.info("Registered new user chat_id=%s", chat_id)

    if message.text.startswith("/start"):
        out = "Я бот, который умеет перекодировать аудио сообщения в текст.\n"
        out += "Я могу раскодировать аудио сообщения на английском 🇬🇧 и русском 🇷🇺 языках. По умолчанию работаю с русским 🇷🇺, но "
        out += "ты всегда можешь изменить язык в настройках /settings."

    elif message.text.startswith("/lang"):
        result = get_user_lang(chat_id)
        if result == "ru-RU":
            out = "Текущий язык 🇷🇺"
        else:
            out = "Текущий язык 🇬🇧"

    elif message.text.startswith("/settings"):
        bot.send_message(chat_id, text="Языковые настройки:", reply_markup=keyboard)
        return

    elif message.text.startswith("/help"):
        out = "Привет 👋. Несмотря на то, что Кирилл и Мефодий создали письменность в начале 860-х годов, "
        out += "кто-то еще 😠 продолжает пользоваться голосовыми сообщениями в чатах. Моя миссия - помочь тебе в раскодировании таких сообщений.\n"
        out += "Просто поделись со мной аудиосообщением и ты получишь в ответ текст."

    else:
        out = "❌ Неправильный тип сообщения. Я могу принять только аудио сообщение."

    bot.reply_to(message, out)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    logger.info("Callback from user_id=%s, data=%s", user_id, call.data)
    out = ""

    if call.data == "ru":
        result = get_user_lang(chat_id=user_id)
        if result == "ru-RU":
            out = "Текущий язык уже 🇷🇺"
        else:
            if set_user_lang(chat_id=user_id, lang="ru-RU"):
                out = "Язык успешно изменен на 🇷🇺"
                logger.info("Language changed to ru-RU for user_id=%s", user_id)
            else:
                out = "Ошибка изменения языка. Попробуйте позже."
                logger.warning("Failed to set lang ru-RU for user_id=%s", user_id)

    elif call.data == "en":
        result = get_user_lang(chat_id=user_id)
        if result == "en-EN":
            out = "Текущий язык уже 🇬🇧"
        else:
            if set_user_lang(chat_id=user_id, lang="en-EN"):
                out = "Язык успешно изменен на 🇬🇧"
                logger.info("Language changed to en-EN for user_id=%s", user_id)
            else:
                out = "Ошибка изменения языка. Попробуйте позже."
                logger.warning("Failed to set lang en-EN for user_id=%s", user_id)

    bot.send_message(user_id, out)


logger.info("Starting bot polling...")
bot.polling()