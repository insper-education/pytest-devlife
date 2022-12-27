
import os
import sys

from dotenv import load_dotenv

from pytest_devlife.fixtures import *
from pytest_devlife.plugin import DevLifePyTestPlugin
from pytest_devlife.settings import load_settings


load_dotenv('.env')


def pytest_configure(config):
    sys.path.append(os.getcwd())
    try:
        settings = load_settings()
        config.pluginmanager.register(DevLifePyTestPlugin(settings))
    except RuntimeError:
        pass
