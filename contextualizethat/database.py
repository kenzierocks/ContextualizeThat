from abc import ABC, abstractmethod


class Database(ABC):
    @abstractmethod
    def __getitem__(self, item):
        raise NotImplementedError()

    @abstractmethod
    def __setitem__(self, key, value):
        raise NotImplementedError()

    @abstractmethod
    def initialize(self, key, default_value):
        raise NotImplementedError()

    def close(self):
        pass


class DictDatabase(Database):
    def __init__(self):
        self._db = dict()

    def __setitem__(self, key, value):
        self._db[key] = value

    def __getitem__(self, item):
        return self._db[item]

    def initialize(self, key, default_value):
        self._db.setdefault(key, default_value)
