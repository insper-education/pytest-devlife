
import pytest
import os
import sys


from pytest_devlife.client import post_solution

from pytest_devlife.fixtures import *
from pytest_devlife.exercise import Exercise
from pytest_devlife.settings import load_settings
from pytest_devlife.constants import SECTION_NAME, BLUE, FAIL, ENDC


class DevLifePyTestPlugin:
    def __init__(self, settings):
        self.exercise_results = {}
        self.messages = []
        self.settings = settings

    def submit_solution(self, exercise):
        title = exercise.meta.get("title")
        result_count = f'{exercise.outcomes.passed()}/{exercise.total_tests()}'
        msg_submitted = f'{title} ({result_count}) {BLUE}[submitted]{ENDC}'
        msg_not_submitted = f'{title} ({result_count}) {BLUE}[not submitted]{ENDC}'

        if not self.settings:
            self.messages.append(msg_not_submitted)
            return
        hostname = self.settings['hostname']
        token = self.settings['token']

        if post_solution(exercise, hostname, token):
            self.messages.append(msg_submitted)
        else:
            self.messages.append(msg_not_submitted)

    def get_or_create_exercise_result(self, item):
        try:
            exercise = Exercise(item)
            slug = exercise.slug
            self.exercise_results.setdefault(slug, exercise)
            return self.exercise_results[slug]
        except RuntimeError as e:
            self.messages.append(f'{item.nodeid}:\t{FAIL}{e}{ENDC}')
        return None

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, items):
        syntax_error_mark = pytest.mark.skip(reason='A syntax error was found')
        for item in items:
            exercise = self.get_or_create_exercise_result(item)
            if not exercise:
                continue
            

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item):
        # execute all other hooks to obtain the report object
        outcome = yield
        rep = outcome.get_result()

        if rep.when == 'call':
            exercise = self.get_or_create_exercise_result(item)
            if exercise:
                exercise.outcomes.increment(rep.outcome)

    def pytest_sessionfinish(self):
        if not self.settings:
            return
        
        for exercise in self.exercise_results.values():
            if len(exercise.outcomes.outcomes) > 0:
                self.submit_solution(exercise)

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.ensure_newline()
        terminalreporter.section(SECTION_NAME, sep='-', blue=True, bold=True)
        terminalreporter.line(os.linesep.join(self.messages))


def pytest_configure(config):
    sys.path.append(os.getcwd())
    try:
        settings = load_settings()
        config.pluginmanager.register(DevLifePyTestPlugin(settings))
    except RuntimeError:
        pass
