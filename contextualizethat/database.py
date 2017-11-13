import codecs
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
    @staticmethod
    def get_db_folder() -> Path:
        return util.get_ready_made_dir(Path.home() / '.config' / NAME / 'db', config.database_folder)

    def __init__(self, name: str):
        self._db = TinyDB(path=TinyDatabase.get_db_folder() / (name + ".json"))
        self.db: Table = self._db.table()

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

    def close(self):
        self._db.close()
        self.db = None

    @staticmethod
    def _unpack(b64_data: str):
        bin_data = codecs.decode(b64_data.encode('ascii'), 'base64')
        value = pickle.loads(bin_data)
        return value

    @staticmethod
    def _pack(value):
        bin_data = pickle.dumps(value)
        b64_data = codecs.encode(bin_data, 'base64').decode('ascii')
        return b64_data


class DictDatabase(Database):
    def __init__(self):
        self._db = dict()

    def __getitem__(self, key):
        return self._db[key]

    def __setitem__(self, key, value):
        self._db[key] = value

    def initialize(self, key, default_value):
        self._db.setdefault(key, default_value)
