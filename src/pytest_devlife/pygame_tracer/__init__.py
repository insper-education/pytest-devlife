from types import BuiltinFunctionType, FunctionType
from typing import Any
import sys

class MockFunction:
    def __init__(self, mod, name, callable):
        self.name = name
        self.mock_module = mod
        self.callable = callable
        self.next_return_value = []
        self.call_limit = -1

    def __call__(self, *args, **kwargs):
        self.mock_module.methods_called.append((self.name, args, kwargs))
        self.call_limit -= 1
        if self.call_limit == -1:
            raise PermissionError(f'{self.name} foi chamado mais que {self.call_limit} vezes')
        if should_call_pygame and not self.next_return_value:
            return self.callable(*args, **kwargs)

        try:
            next_return_value = self.next_return_value.pop(0)
            return next_return_value
        except IndexError:
            return None


class MockWrapper:
    def __init__(self, original_module):
        self.original_module = original_module
        self.methods_called = []

    def __getattr__(self, name):
        if self.original_module:
            original = getattr(self.original_module, name)
            if type(original) in [FunctionType, BuiltinFunctionType]:
                value = MockFunction(self, name, original)
                setattr(self, name, value)
                return value
            return original

        value = MockFunction(self, name, lambda t: 0)
        setattr(self, name, value)
        return value


def function_was_called(object, funcname):
    for m in object.methods_called:
        if m[0] == funcname:
            return m
    return None


def reset_state():
    mock.methods_called = []
    mock.display.methods_called = []


try:
    import pygame

    mock = MockWrapper(pygame)
    mock.display = MockWrapper(pygame.display)
    mock.image = MockWrapper(pygame.image)
    mock.event = MockWrapper(pygame.event)

    should_call_pygame = True
    sys.modules['pygame'] = mock
    reset_state()
except ModuleNotFoundError:
    pass