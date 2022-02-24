import ast
import traceback
from pathlib import Path
import yaml
import mimetypes
import glob
import os.path as osp


class Outcomes:
    def __init__(self):
        self.outcomes = {}

    def passed(self):
        return self.outcomes.get('passed', 0)

    def total(self):
        return sum(self.outcomes.values())

    def increment(self, outcome_name):
        self.outcomes.setdefault(outcome_name, 0)
        self.outcomes[outcome_name] += 1


class Exercise:
    def __init__(self, item):
        self.exercise_dir = Path(item.fspath).parent
        self.outcomes = Outcomes()

        self.meta = self._load_meta(self.exercise_dir)
        self.code = self._load_student_submission()

        self._check_meta()
        #self._check_code()

    def to_data(self):
        passed = self.outcomes.passed()
        total = self.total_tests()
        return {
            'slug': self.slug,
            'points': passed / total,
            'test_results': {'passed': f'{passed}/{total}'},
            'student_input': self.code,
        }

    def total_tests(self):
        # Skipped tests are not included in the outcomes
        return self.outcomes.total()

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
        # We only check the syntax if the student file is a Python file
        if '.py' not in Path(self.code_file).suffix:
            return
        try:
            compile(self.code, filename=self.code_file, mode='exec', flags=ast.PyCF_ONLY_AST)
        except SyntaxError:
            msg = traceback.format_exc()
            self.error_msg = msg  # TODO DO WE NEED THIS MESSAGE FOR ANYTHING?
            self.syntax_ok = False

    def _load_meta(self, exercise_dir):
        prev_dir = None
        curr_dir = exercise_dir

        while curr_dir and curr_dir != prev_dir:
            meta_file = curr_dir / 'meta.yml'
            try:
                with open(meta_file) as f:
                    self.meta_file = meta_file
                    return yaml.safe_load(f)
            except IOError:
                prev_dir = curr_dir
                curr_dir = curr_dir.parent
        raise RuntimeError('Could not find meta.yml in exercise folder')

    def _load_student_submission(self):
        files_to_send = {}
        for file in  glob.glob(str(self.exercise_dir) + '/**', recursive=True):
            # Exclusion rules
            if osp.isdir(file): continue # not a directory
            if Path(file).name.startswith('test_'): continue # not a test file
            if file.endswith('.md'): continue # not a markdown file

            mtype, _ = mimetypes.guess_type(file)
            if mtype and mtype.startswith('text/'):
                with open(file) as f:
                    key = Path(file).relative_to(self.exercise_dir)
                    files_to_send[str(key)] = f.read()

        return files_to_send
