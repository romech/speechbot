import shelve
import time

_PATH = "data.db"
with shelve.open(_PATH) as db:
    if 'cooldown' not in db:
        db['voices'] = {}
        db['cooldown'] = {}


def set_voice(uid, choice):
    """Choose Trump/Female"""
    with shelve.open(_PATH, writeback=True) as db:
        db['voices'][uid] = choice


def get_voice(uid):
    """Get None or voice"""
    with shelve.open(_PATH) as db:
        return db['voices'].get(uid)


def set_cooldown(uid, cooldown):
    """Don't let user submit too many recordings"""
    with shelve.open(_PATH, writeback=True) as db:
        db['cooldown'][uid] = time.time() + cooldown


def check_cooldown(uid):
    with shelve.open(_PATH) as db:
        return db['cooldown'].get(uid, 0) < time.time()
