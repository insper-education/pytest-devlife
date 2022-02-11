from pathlib import Path
import os
import os.path as osp
import json

def _load_settings_from_disk():
    try:
        settings_file = Path.home() / 'DevLife' / '.vscode' / 'settings.json'
        with open(settings_file) as f:
            settings = json.load(f)
            return {
                'token': settings['insper.token'],
                'hostname': settings['insper.hostname']
            }
    except:
        raise RuntimeError()

def load_settings():
    token = os.getenv('AUTH_TOKEN')
    hostname = os.getenv('AUTH_HOSTNAME')
    if not token or not hostname:
        return _load_settings_from_disk()
    return {
        'token': token,
        'hostname': hostname
    }
