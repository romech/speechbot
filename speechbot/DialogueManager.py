import random

import yaml

from telebot import types

dialogues = yaml.load(open('dialogues.yaml', 'r'))

_text_topic = { text: topic for (topic, choices) in dialogues['keyboards'].items() for text in choices }


def get_replica(topic, message=None):
    if message:
        print(message)

    if topic in dialogues:
        found = dialogues[topic]
        replica = found if isinstance(found, str) else random.choice(dialogues[topic])
    else:
        replica = random.choice(dialogues['undefined'])

    if '$' in replica:
        replica = replica.replace('$username', message.from_user.first_name)
        # and maybe some other substitutions

    return replica


def infer_topic(message):
    return _text_topic.get(message.text)


def get_keyboard(topic):
    if topic is None:
        return types.ReplyKeyboardRemove()

    else:
        markup = types.ReplyKeyboardMarkup()
        markup.add(*(types.KeyboardButton(choice) for choice in dialogues['keyboards'][topic]))

        return markup


def get_sticker(theme):
    return random.choice(dialogues['stickers'][theme])
