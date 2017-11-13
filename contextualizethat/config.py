import os
from pathlib import Path
from typing import List

from . import algo as _algo
from .auth import Auth
from .consts import NAME
from .database import Database, DictDatabase
from .errorpolicy import ErrorPolicy, ExponentialBackOffErrorPolicy

# Defaults for config values
url = dict(host='example.com', port=8065, basepath='/api/v4')
authentication: Auth = None
error_policy: ErrorPolicy = ExponentialBackOffErrorPolicy()
channels: List[str] = []
reply_messages: List[str] = [
    '''
    Can you _contextualize that_?
    ''',
    '''
    Sorry to interrupt, but can you _contextualize that_?
    ''',
    '''
    Hold on a minute. Please _contextualize that_!
    '''
]
algo = _algo.default_algo()
database_folder = None


def database(name: str) -> Database:
    return DictDatabase()


def _get_config_path() -> Path:
    xdg_config_dir = Path.home() / '.config'
    xcd_env = os.environ.get('XDG_CONFIG_DIR', '')
    if xcd_env:
        xdg_config_dir = Path(xcd_env)
    p = xdg_config_dir / NAME
    p.mkdir(parents=True, exist_ok=True)
    return p / 'config.py'


_cfg_path = _get_config_path()
if _cfg_path.exists():
    _config = _cfg_path.read_text('utf-8')
    exec(_config)
