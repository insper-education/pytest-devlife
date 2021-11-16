from pathlib import Path
import os


def load_settings():
    token = os.getenv('AUTH_TOKEN')
    hostname = os.getenv('AUTH_HOSTNAME')
    if not token or not hostname:
        raise RuntimeError()
    return {
        'token': token,
        'hostname': hostname
    }
