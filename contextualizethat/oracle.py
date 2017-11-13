import enum
from enum import Enum
from itertools import chain
from typing import Iterable, List, Optional

from .database import Database
from .message import Message

# Keep 10 minutes of messages
RECENT_TIME_WINDOW = 10 * 60
# Keep many thousands of message counts for good measure
COUNTS = 100000


class Key(Enum):
    RECENT_MESSAGES = enum.auto()
    MESSAGE_COUNTS = enum.auto()


def _message_time(m: Message):
    return m.time


class ChatOracle:
    """
    An "oracle" for chat information. Keeps track of how frequently people are talking.
    Unlike Oracle, this actually functions well.
    """

    def __init__(self, db: Database):
        self.db = db

        db.initialize(Key.RECENT_MESSAGES.name, [])
        db.initialize(Key.MESSAGE_COUNTS.name, [])

    @property
    def _recents(self) -> List[Message]:
        return self.db[Key.RECENT_MESSAGES.name]

    @_recents.setter
    def _recents(self, recents: List[Message]):
        self.db[Key.RECENT_MESSAGES.name] = recents

    def get_latest_message(self) -> Optional[Message]:
        if len(self._recents) == 0:
            return None
        return self._recents[-1]

    def get_num_messages(self):
        return len(self._recents)

    @property
    def _counts(self) -> List[int]:
        return self.db[Key.MESSAGE_COUNTS.name]

    @_counts.setter
    def _counts(self, counts: List[int]):
        self.db[Key.MESSAGE_COUNTS.name] = counts

    def get_message_counts(self):
        return self._counts

    def feed_messages(self, messages: Iterable[Message]):
        if not messages:
            return
        self._update_recent(messages)
        self._add_counts()

    def _update_recent(self, messages: Iterable[Message]):
        recents = self._recents

        messages = sorted(messages, key=_message_time)

        t = messages[-1].time - RECENT_TIME_WINDOW

        def time_check(m: Message):
            return m.time >= t

        combined = list(filter(time_check, chain(recents, messages)))

        self._recents = combined

    def _add_counts(self):
        counts = self._counts

        counts.append(len(self._recents))

        while len(counts) > COUNTS:
            counts.pop(0)

        self._counts = counts
