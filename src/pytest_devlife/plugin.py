import os

import pytest

from pytest_devlife.client import post_solution
from pytest_devlife.constants import SECTION_NAME
from pytest_devlife.exercise import Exercise


class DevLifePyTestPlugin:
    def __init__(self, settings):
        self.exercise_results = {}
        self.messages = []
        self.settings = settings

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, items):
        for item in items:
            exercise = self.__get_or_create_exercise_result(item)
            if not exercise:
                continue

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item):
        # execute all other hooks to obtain the report object
        outcome = yield
        rep = outcome.get_result()

        if rep.when == 'call' or (rep.when == 'setup' and rep.outcome == 'failed'):
            exercise = self.__get_or_create_exercise_result(item)
            if exercise:
                exercise.outcomes.increment(rep.outcome)

    def pytest_sessionfinish(self):
        if not self.settings:
            return

        for exercise in self.exercise_results.values():
            if len(exercise.outcomes.outcomes) > 0:
                self.__submit_solution(exercise)

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.ensure_newline()
        terminalreporter.section(SECTION_NAME, sep='-', blue=True, bold=True)
        terminalreporter.line(os.linesep.join(self.messages))

    def __get_or_create_exercise_result(self, item):
        try:
            exercise = Exercise(item)
            slug = exercise.slug
            if not slug:
                return None
            self.exercise_results.setdefault(slug, exercise)
            return self.exercise_results[slug]
        except RuntimeError as e:
            self.messages.append(f'{item.nodeid}:\t{e}')
        return None

    def __submit_solution(self, exercise):
        title = exercise.meta.get("title")
        result_count = f'{exercise.outcomes.passed()}/{exercise.total_tests()}'
        exercise_data = f'{title} ({result_count})'

        token = self.settings['token']

        if post_solution(exercise, token):
            self.messages.append(f'{exercise_data} [submitted]')
        else:
            self.messages.append(f'{exercise_data} [not submitted]')
