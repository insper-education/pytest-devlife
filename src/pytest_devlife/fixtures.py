import builtins
import io
import pytest
import runpy
import pytest_devlife.pygame_tracer


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


@pytest.fixture
def mockgame():
    return pytest_devlife.pygame_tracer.mock
