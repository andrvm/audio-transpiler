# !/usr/bin/env python
import os
import uuid
import telebot
import speech_recognition as sr
from pydub import AudioSegment

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get('APP_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['audio', 'voice'])
def handle_voice(message):

    out = 'Сорри, но что-то пошло не так...'
    unique_name = uuid.uuid4()
    wav_file = f'{unique_name}.wav'
    ogg_file = f'{unique_name}.ogg'

    if message.content_type == 'audio':
        file_info = bot.get_file(message.audio.file_id)
    else:
        file_info = bot.get_file(message.voice.file_id)

    downloaded_file = bot.download_file(file_info.file_path)
    with open(ogg_file, 'wb') as new_file:
        new_file.write(downloaded_file)

    # transpile
    sound = AudioSegment.from_ogg(ogg_file)
    sound.export(wav_file, format='wav')
    #
    r = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        audio = r.record(source)
        out = r.recognize_google(audio, language='ru-RU')

    # clean
    if os.path.exists(wav_file):
        os.remove(wav_file)

    if os.path.exists(ogg_file):
        os.remove(ogg_file)

    bot.reply_to(message, out)


@bot.message_handler(
    content_types=[content_type for content_type in ['text', 'document', 'sticker', 'photo', 'video'] if
                   content_type not in ['audio', 'voice']])
def handle_data(message):
    if message.text.startswith('/help'):
        out = 'Привет 👋. Несмотря на то, что Кирилл и Мефодий создали письменность в начале 860-х годов\n'
        out += 'кто-то еще 😠 продолжает пользоваться голосовыми сообщениями в чатах. Моя миссия - помочь тебе в раскодировании таких сообщений.\n'
        out += 'Просто поделись со мной аудиосообщением и ты получишь в ответ текст.'
    else:
        out = '❌ Неправильный тип сообщения. Я могу принять только аудио сообщение.'

    bot.reply_to(message, out)


bot.polling()
