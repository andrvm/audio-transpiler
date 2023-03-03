# !/usr/bin/env python
import telebot
import speech_recognition as sr
from pydub import AudioSegment

bot = telebot.TeleBot('6294396825:AAEo59o8skQLoyn4vYPtK0PtEVsz3TkiIVQ')

AUDIO_FILE = 'audio.wav'


@bot.message_handler(content_types=['audio', 'voice'])
def handle_voice(message):
    out = 'Сорри, но что-то пошло не так...'

    if message.content_type == 'audio':
        file_info = bot.get_file(message.audio.file_id)
    else:
        file_info = bot.get_file(message.voice.file_id)

    downloaded_file = bot.download_file(file_info.file_path)
    with open('audio.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)

    # transpile
    sound = AudioSegment.from_ogg('audio.ogg')
    sound.export(AUDIO_FILE, format='wav')
    #
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)
        out = r.recognize_google(audio, language='ru-RU')
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
