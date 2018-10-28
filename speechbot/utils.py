def telebot_fallback():
    def decorate(f):
        def applicator(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                print("Recovered from Telebot's exception.\n", e)

        return applicator

    return decorate
