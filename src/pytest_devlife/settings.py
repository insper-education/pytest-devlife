from pathlib import Path
import yaml


def load_settings():
    with open(Path.home() / '.devlife' / 'settings.yml') as f:
        settings = yaml.safe_load(f)
    if settings.get('token') is None:
        raise RuntimeError('Could not find token in ~/.devlife/settings.yml')
    if settings.get('hostname') is None:
        raise RuntimeError('Could not find hostname in ~/.devlife/settings.yml')
    return settings
