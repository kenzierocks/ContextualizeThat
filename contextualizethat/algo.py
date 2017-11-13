import random
import time
from abc import ABC, abstractmethod
from typing import Iterable, Callable

from .oracle import ChatOracle


class Algo(ABC):
    @abstractmethod
    def send_context_message(self, info: ChatOracle) -> bool:
        raise NotImplementedError()


class SequenceAlgo(Algo):
    """
    Applies an operation to the result of the algorithm sequence.
    """

    @staticmethod
    def or_seq(sequence: Iterable[Algo]):
        """
        Applies OR to the sequence.
        """
        return SequenceAlgo(sequence, any)

    @staticmethod
    def and_seq(sequence: Iterable[Algo]):
        """
        Applies AND to the sequence.
        """
        return SequenceAlgo(sequence, all)

    def __init__(self, sequence: Iterable[Algo], operation: Callable[[Iterable[bool]], bool]):
        self.sequence = sequence
        self.operation = operation

    def send_context_message(self, *args, **kwargs) -> bool:
        return self.operation(seq.send_context_message(*args, **kwargs) for seq in self.sequence)


class HighWordCountAlgo(Algo):
    """
    Watches for a small number of users to generate higher than average word counts, then sends out a TRUE.
    Returns FALSE when things return to normal.
    """
    pass


class LongThreadAlgo(Algo):
    """
    Watches for long threads of messages, then sends out a TRUE.
    Returns FALSE when a thread appears to have ended.
    """
    # Limit for deviation from COUNTS mean
    # More than this -> return true
    _DEVIATION_FACTOR = 0.25

    def send_context_message(self, info: ChatOracle) -> bool:
        counts = info.get_message_counts()
        if not counts:
            return False
        # compute mean
        mean = sum(counts) / len(counts)
        # compute mean of diffs from mean
        mean_of_diffs = sum(abs(c - mean) for c in counts) / len(counts)
        # compute diff from {last diff} to {mean of diffs}
        # take sqrt to minimize it!
        deviation = abs(abs(counts[-1] - mean) - mean_of_diffs) ** (1 / 2)
        return deviation > LongThreadAlgo._DEVIATION_FACTOR


class DelayAlgo(Algo):
    """
    Simply applies a delay since the last call.
    """
    DEFAULT_DELAY = 30 * 60

    def __init__(self, delay=DEFAULT_DELAY):
        self.delay = delay
        self._last_time = 0

    def send_context_message(self, info: ChatOracle) -> bool:
        current_time = time.time()
        delta = current_time - self._last_time
        if delta >= self.delay:
            self._last_time = current_time
            return True
        return False


class RandoAlgo(Algo):
    """
    Randomizes the return value.
    """

    def __init__(self, chance: float):
        """
        :param chance: Percent chance of TRUE. [0, 1).
        """
        self.chance = chance

    def send_context_message(self, info: ChatOracle) -> bool:
        return random.random() >= self.chance


_DEFAULT_ALGO = SequenceAlgo.and_seq((LongThreadAlgo(), DelayAlgo(), RandoAlgo(75)))


def default_algo() -> Algo:
    """
    The default algorithm. It may vary.
    :return: the default algorithm
    """
    return _DEFAULT_ALGO
