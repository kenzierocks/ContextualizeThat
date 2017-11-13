import pickle
from abc import ABC, abstractmethod
from pathlib import Path

from tinydb import where
from tinydb.database import Table, TinyDB

from . import config, util
from .consts import NAME


class Database(ABC):
    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError()

    @abstractmethod
    def __setitem__(self, key, value):
        raise NotImplementedError()

    @abstractmethod
    def initialize(self, key, default_value):
        raise NotImplementedError()

    def close(self):
        pass


class TinyDatabase(Database):
    DATABASE_FOLDER = util.get_ready_made_dir(Path.home() / '.config' / NAME / 'db', config.database_folder)

    def __init__(self, name: str):
        self.db: Table = TinyDB(path=TinyDatabase.DATABASE_FOLDER / name + ".json").table()

    def __getitem__(self, key):
        bin_data = self.db.get(where('key') == key)['value']
        return TinyDatabase._unpack(bin_data)

    def __setitem__(self, key, value):
        record = dict(key=key, value=TinyDatabase._pack(value))
        self.db.upsert(record, where('key') == key)

    def initialize(self, key, default_value):
        if self.db.contains(where('key') == key):
            return
        self[key] = default_value

    @staticmethod
    def _unpack(value):
        return pickle.loads(value)

    @staticmethod
    def _pack(value):
        return pickle.dumps(value)


class DictDatabase(Database):
    def __init__(self):
        self._db = dict()

    def __getitem__(self, key):
        return self._db[key]

    def __setitem__(self, key, value):
        self._db[key] = value

    def initialize(self, key, default_value):
        self._db.setdefault(key, default_value)
