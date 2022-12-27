import glob
import mimetypes
import os.path as osp
from pathlib import Path

import yaml

META_FILENAME = 'devlife.yml'


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

    def to_data(self):
        passed = self.outcomes.passed()
        total = self.total_tests()

        points = 0
        if total > 0:
            points = passed / total

        return {
            'exercise': {
                'course': self.course,
                'slug': self.slug,
                'tags': self.tags,
            },
            'points': points,
            'log': {
                'passing_tests': passed,
                'total_tests': total,
                'student_input': self.code,
            },
        }

    def total_tests(self):
        # Skipped tests are not included in the outcomes
        return self.outcomes.total()

    def has_syntax_errors(self):
        return not self.syntax_ok

    @property
    def slug(self):
        return self.meta.get('slug', '')

    @property
    def course(self):
        return self.meta.get('course')

    @property
    def tags(self):
        return self.meta.get('tags', [])

    @property
    def telemetry_endpoint(self):
        return self.meta.get('telemetryEndpoint')

    def meta_is_valid(self):
        if not self.meta:
            print(f'Could not find {META_FILENAME} file')
            return False
        if self.slug is None:
            print(f'Could not find slug in {META_FILENAME}')
            return False
        if self.course is None:
            print(f'Could not find course in {META_FILENAME}')
            return False
        return True

    def _load_meta(self, exercise_dir):
        prev_dir = None
        curr_dir = exercise_dir

        while curr_dir and curr_dir != prev_dir:
            meta_file = curr_dir / META_FILENAME
            try:
                with open(meta_file, encoding='utf8', errors='replace') as f:
                    self.meta_file = meta_file
                    return yaml.safe_load(f)
            except IOError:
                prev_dir = curr_dir
                curr_dir = curr_dir.parent
        raise {}

    def _load_student_submission(self):
        files_to_send = {}
        for file in  glob.glob(str(self.exercise_dir) + '/**', recursive=True):
            # Exclusion rules
            if osp.isdir(file): continue # not a directory
            if Path(file).name.startswith('test_'): continue # not a test file
            if file.endswith('.md'): continue # not a markdown file

            mtype, _ = mimetypes.guess_type(file)
            if mtype and mtype.startswith('text/'):
                with open(file, encoding='utf8', errors='replace') as f:
                    key = Path(file).relative_to(self.exercise_dir)
                    files_to_send[str(key)] = f.read()

        return files_to_send
