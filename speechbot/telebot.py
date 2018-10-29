import random
import tempfile
import time

import requests
import telebot
import yaml
from telebot import apihelper

import speechbot.DialogueManager as texting
import speechbot.persistent as db
from speechbot.utils import *

connection_settings = yaml.load(open('connect-keys.yaml', 'r'))

# connect-keys.yaml file
#
# connection:
#   token: 'T0KEИ'
#   proxy:
#     https: 'socks5://uid:pwd@host:port'
#
# endpoints:
#   Trump: 'http://host/voice1'
#   Robot: 'http://host/voice2'
#   ...
#
# duration-limit: 300
#

apihelper.proxy = connection_settings['proxy']

bot = telebot.TeleBot(connection_settings['token'])


def reply(message, topic=None, reply_markup=None):
    bot.send_message(message.chat.id, texting.get_replica(topic, message), reply_markup=reply_markup)


def log_message(message):
    print('@{}:'.format(message.from_user.username), message.json)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
@telebot_fallback()
def send_welcome(message):
    voice = db.get_voice(message.chat.id)
    if (voice is None) or (message.text == '/help'):
        reply(message, 'newcomer-help')
        prompt_voice(message)

    else:
        reply(message, 'greeting')


@bot.message_handler(commands=['voice'])
@telebot_fallback()
def prompt_voice(message):
    reply(message, 'choose-voice', texting.get_keyboard('choose-voice'))


@bot.message_handler(func=texting.infer_topic)
@telebot_fallback()
def follow_up(message):
    # print('I have recognized topic!')
    topic = texting.infer_topic(message)

    if topic == 'choose-voice':
        db.set_voice(message.chat.id, message.text.split()[0])

        reply(message, 'changed-voice', texting.get_keyboard(None))

#   else if topic == ???:
#       ...


@bot.message_handler(func=lambda message: True)
@telebot_fallback()
def echo_message(message):
    log_message(message)
    reply(message)


@bot.message_handler(content_types=['voice'])
def handle_docs_audio(message):
    if message.voice.duration > connection_settings['duration-limit']:
        reply(message, 'duration-exceeded')
    else:
        any_audio_handler(message, message.voice.file_id)


@bot.message_handler(content_types=['audio'])
def handle_docs_audio(message):
    if message.voice.duration > connection_settings['duration-limit']:
        reply(message, 'duration-exceeded')
    else:
        any_audio_handler(message, message.audio.file_id)


@telebot_fallback()
def any_audio_handler(message, voice):
    log_message(message)

    if not db.check_cooldown(message.chat.id):
        reply(message, 'ddos')
        print(message.chat.username, 'is sending audio too frequently')
        return

    if (db.get_voice(message.chat.id) == 'Trump') and (random.random() < 0.5):
        bot.send_sticker(message.chat.id, texting.get_sticker('trump'))
    reply(message, 'loading')

    try:
        file_id = voice
        tg_voice = bot.download_file(bot.get_file(file_id).file_path)
    except Exception as e:
        print("Unable to load user's voice.\n", e)
        reply(message, 'failed-voice-download', texting.get_keyboard(None))
        return

    db.set_cooldown(message.chat.id, 15)

    try:
        voice_downloaded = tempfile.NamedTemporaryFile(suffix=".ogg")
        voice_downloaded.write(tg_voice)
        voice_downloaded.seek(0)
        response = requests.post(connection_settings['endpoints'][db.get_voice(message.chat.id)],
                                 data={"voice": db.get_voice(message.chat.id) or 'Female'},
                                 files={"file": voice_downloaded})

    except Exception as e:
        print('Unable to upload voice!\n', e)
        reply(message, 'failed-server-request')
        bot.send_sticker(message.chat.id, texting.get_sticker('trump-ttl'))

    else:
        if response.status_code == 200:
            # bot.send_message(message.chat.id, 'Готово!')

            with open("modified.wav", 'wb') as f:
                f.write(response.content)

            bot.send_voice(message.chat.id, open("modified.wav", 'rb'))

        else:
            reply(message, 'failed-server-request', texting.get_keyboard(None))
            bot.send_sticker(message.chat.id, texting.get_sticker('trump-ttl'))
            print('Unsuccessful request to upload voice, status code:', response.status_code)
            print('Caused by:', response.request)

    finally:
        voice_downloaded.close()


@bot.message_handler(content_types=['sticker'])
@telebot_fallback()
def handle_sticker(message):
    print(message.sticker.file_id)
    reply(message, 'thank-for-sticker')


@bot.message_handler(content_types=['document', 'photo', 'video', 'video_note', 'location', 'contact'])
def handle_docs_audio(message):
    try:
        fname = message.document.file_name
        if fname.endswith('.wav'):
            if message.voice.duration > connection_settings['duration-limit']:
                reply(message, 'duration-exceeded')
            else:
                any_audio_handler(message, message.document.file_id)
            return
    except:
        pass

    reply(message, 'unknown-datatype')


while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print('Bot shut down and restarted. Cause:\n', e)
        time.sleep(15)
