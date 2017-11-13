from abc import ABC, abstractmethod


class ErrorPolicy(ABC):
    @abstractmethod
    def accept_error(self, error: Exception) -> float:
        raise NotImplementedError()


class ExponentialBackOffErrorPolicy(ErrorPolicy):
    def __init__(self, base=2, factor=0.25):
        self.base = base
        self.factor = factor
        self._errors = 0

    @property
    def _sleep_time(self):
        # base raised to factor times errors
        return self.base ** (self.factor * self._errors)

    def accept_error(self, error: Exception) -> float:
        self._errors += 1
        return self._sleep_time
