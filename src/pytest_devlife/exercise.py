import ast
import traceback
from pathlib import Path
import yaml


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
