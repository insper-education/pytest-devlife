import builtins
import pytest
import io
import os
import runpy
import ast
import yaml
import requests
import traceback
from pathlib import Path
import sys


SECTION_NAME = 'Developer Life'
# FONT CONSTANTS
BLUE = '\033[94m'
CYAN = '\033[96m'
GREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


################ FIXTURES ################

inpt = builtins.input
@pytest.fixture
def mock_input(monkeypatch):
    def mocked(prompt=''):
        return inpt()

    def setup_mock(strings):
        monkeypatch.setattr('sys.stdin', io.StringIO('\n'.join(strings)))

    monkeypatch.setattr('builtins.input', mocked)
    return setup_mock


@pytest.fixture
def run_program(capsys):
    def runner(filename):
        try:
            runpy.run_path(filename)
        except EOFError:
            stdout, _ = capsys.readouterr()
            pytest.fail(f'Your program called input() more times than expected. The program should have already ended. The output was:\n{stdout}')
    return runner


################ UTILS ################

class Outcomes:
    def __init__(self):
        self.outcomes = {}

    def passed(self):
        return self.outcomes.get('passed', 0)

    def increment(self, outcome_name):
        self.outcomes.setdefault(outcome_name, 0)
        self.outcomes[outcome_name] += 1


class Exercise:
    def __init__(self, item):
        exercise_dir = Path(item.fspath).parent
        self.meta_file = exercise_dir / 'meta.yml'
        self.code_file = exercise_dir / 'solution.py'
        self.total_tests = 0
        self.outcomes = Outcomes()

        self.meta = self._load_meta()
        self.code = self._load_code()

        self._check_meta()
        self._check_code()

    def to_data(self):
        passed = self.outcomes.passed()
        total = self.total_tests
        return {
            'slug': self.slug,
            'points': passed / total,
            'summary': {'passed': f'{passed}/{total}'},
            'long_answer': {'code': self.code},
        }

    def inc_tests(self):
        self.total_tests += 1

    def has_syntax_errors(self):
        return not self.syntax_ok

    @property
    def slug(self):
        return self.meta.get('slug')

    @property
    def offering(self):
        return self.meta.get('offering')

    def _check_meta(self):
        if self.slug is None:
            raise RuntimeError('Could not find slug in meta.yml')
        if self.offering is None:
            raise RuntimeError('Could not find offering in meta.yml')

    def _check_code(self):
        self.syntax_ok = True
        try:
            compile(self.code, filename=self.code_file, mode='exec', flags=ast.PyCF_ONLY_AST)
        except SyntaxError:
            msg = traceback.format_exc()
            self.error_msg = msg  # TODO DO WE NEED THIS MESSAGE FOR ANYTHING?
            self.syntax_ok = False

    def _load_meta(self):
        try:
            with open(self.meta_file) as f:
                return yaml.safe_load(f)
        except IOError:
            raise RuntimeError('Could not find meta.yml in exercise folder')

    def _load_code(self):
        with open(self.code_file) as f:
            return f.read()


def load_settings():
    with open(Path.home() / '.devlife' / 'settings.yml') as f:
        settings = yaml.safe_load(f)
    if settings.get('token') is None:
        raise RuntimeError('Could not find token in ~/.devlife/settings.yml')
    if settings.get('hostname') is None:
        raise RuntimeError('Could not find hostname in ~/.devlife/settings.yml')
    return settings


################ PLUGIN ################

class DevLifePyTestPlugin:
    def __init__(self):
        self.exercise_results = {}
        self.messages = []
        try:
            self.settings = load_settings()
        except (RuntimeError, FileNotFoundError) as e:
            self.settings = None
            self.messages.append(f'{FAIL}{e}{ENDC}')

    def submit_solution(self, exercise):
        title = exercise.meta.get("title")
        result_count = f'{exercise.outcomes.passed()}/{exercise.total_tests}'
        msg_submitted = f'{title} ({result_count}) {BLUE}[submitted]{ENDC}'
        msg_not_submitted = f'{title} ({result_count}) {BLUE}[not submitted]{ENDC}'

        if not self.settings:
            self.messages.append(msg_not_submitted)
            return
        hostname = self.settings['hostname']
        token = self.settings['token']

        try:
            data = exercise.to_data()
            headers = {
                'Authorization': f'Token {token}',
            }
            url = f'{hostname}/api/offerings/{exercise.offering}/exercises/{exercise.slug}/answers/'
            requests.post(url, json=data, headers=headers)
            self.messages.append(msg_submitted)
        except requests.exceptions.ConnectionError:
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
            exercise.inc_tests()
            if exercise.has_syntax_errors():
                exercise.outcomes.increment('errors')
                item.add_marker(syntax_error_mark)

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
            self.submit_solution(exercise)

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.ensure_newline()
        terminalreporter.section(SECTION_NAME, sep='-', blue=True, bold=True)
        terminalreporter.line(os.linesep.join(self.messages))


def pytest_configure(config):
    sys.path.append(os.getcwd())
    config.pluginmanager.register(DevLifePyTestPlugin())
