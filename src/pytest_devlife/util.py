import inspect
from contextlib import contextmanager


def function_exists_in_module(mod, func):
    all_functions = inspect.getmembers(mod, inspect.isfunction)
    assert any([f[0] == func for f in all_functions]), f'A função {func} não foi definida!'


def called_once_with(func, args, kwargs={}):
    args = tuple(args)

    n_calls = len(func.mock_calls)
    assert n_calls == 1, f'{func._extract_mock_name()} só deveria ser chamada uma vez, mas foi chamada {n_calls} vezes'

    received_args = func.mock_calls[0].args
    assert received_args == args, f'{func._extract_mock_name()} deveria receber como argumentos {args}, mas recebeu {received_args}'

    received_kwargs = func.mock_calls[0].kwargs
    if len(received_kwargs) != 0 or len(kwargs) != 0:
        assert func.mock_calls[0].kwargs == kwargs


@contextmanager
def catch_loop_stop_iteration():
    try:
        yield
    except StopIteration:
        raise AssertionError('Seu loop rodou mais vezes que o esperado!')
