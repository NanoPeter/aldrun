"""

"""
from enum import Enum
from threading import Thread
from datetime import datetime

from threading import Event
from typing import Dict, List, Tuple, Union

from abc import ABC, abstractmethod

from time import time, sleep

REGISTRY = {}


def register(name):
    """Decorator to register new recipes and give them global names.

    This function should only be used as a decorator for measurement classes
    which inherit the AbstractMeasurement class.

    :usage:
    @register('My Recipe')
    class MyRecipe(AbstractRecipe):
        ....

    :param name: name of the recipe class
    :return: another decorator to register the class
    """
    def register_wrapper(cls):
        """
        :param cls: recipe class to be registered
        :return: the class which was given by the input
        """
        if issubclass(cls, AbstractRecipe):
            REGISTRY[name] = cls
        return cls
    return register_wrapper


class AbstractValue(object):
    """Represents a generic input which the measurement class will return
    """

    def __init__(self, fullname: str, default: Union[int, float, bool, str, datetime]) -> None:
        """
        :param fullname: name which should be displayed
        :param default: default value
        """
        self.__default = default
        self.__fullname = fullname

    @property
    def default(self) -> Union[int, float, bool, str, datetime]:
        return self.__default

    @property
    def fullname(self) -> str:
        return self.__fullname

    def convert_from_string(self, value: str) -> Union[int, float, bool, str, datetime]:
        NotImplementedError()


class IntegerValue(AbstractValue):
    def __init__(self, fullname: str, default: int = 0) -> None:
        super().__init__(fullname, default)

    def convert_from_string(self, value: str) -> int:
        return int(value)


class FloatValue(AbstractValue):
    def __init__(self, fullname: str, default: float = 0.0) -> None:
        super().__init__(fullname, default)

    def convert_from_string(self, value: str) -> float:
        return float(value)


def logable(text=''):
    def outer_wrapper(foo):
        def inner_wrapper(self, *args, **kwargs):
            self._log(text)
            foo(self, *args, **kwargs)
        return inner_wrapper
    return outer_wrapper


def run_and_wait(foo, total_run_time: float=0):
    def wrapper(*args, **kwargs):
        start_time = time()
        foo(*args, **kwargs)
        foo_run_time = time() - start_time
        time_to_wait = total_run_time - foo_run_time
        if time_to_wait > 0:
            sleep(time_to_wait)
    return wrapper


class AbstractRecipe(ABC):
    """

    """
    def __init__(self):
        self._stop_process = Event()

    def __call__(self):
        self._stop_process.clear()
        self._run()

    def _log(self, text):
        print('{} - {}'.format(datetime.now().isoformat(), text))

    @abstractmethod
    def _run(self):
        pass

    @staticmethod
    @abstractmethod
    def inputs():
        return {}



