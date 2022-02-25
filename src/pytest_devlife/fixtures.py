import builtins
import io
import pytest
import runpy
from unittest import mock
import functools

inpt = builtins.input
@pytest.fixture
def mock_input(monkeypatch):
    def mocked(prompt=''):
        return inpt()

    def setup_mock(strings):
        mocked_stdin =  io.StringIO('\n'.join(strings))
        monkeypatch.setattr('sys.stdin', mocked_stdin)

        return mocked_stdin

    monkeypatch.setattr('builtins.input', mocked)
    return setup_mock


@pytest.fixture
def run_program(capsys):
    def runner(filename):
        try:
            return runpy.run_path(filename)
        except EOFError:
            stdout, _ = capsys.readouterr()
            pytest.fail(f'Your program called input() more times than expected. The program should have already ended. The output was:\n{stdout}')
    return runner


def mockgame(module_name):
    def module_name_decorator(func):
        @functools.wraps(func)
        @mock.patch(module_name)
        def effective_mock_pygame_decorator(mpyg):
            import pygame

            # restore constants
            for att in pygame.__dict__.keys():
                if att.upper() == att:
                    setattr(mpyg, att, getattr(pygame, att))

            func(mpyg)

        return effective_mock_pygame_decorator

    return module_name_decorator
