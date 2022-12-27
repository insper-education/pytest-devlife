import os


def load_settings():
    token = os.getenv('DEVLIFE_TOKEN')
    return {
        'token': token,
    }
