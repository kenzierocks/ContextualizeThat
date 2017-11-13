from abc import ABC, abstractmethod
from typing import Dict, Any


class Auth(ABC):
    @abstractmethod
    def add_authorization_options(self, options: Dict[str, Any]):
        pass


class TokenAuth(Auth):
    def __init__(self, token: str):
        self.token = token

    def add_authorization_options(self, options: Dict[str, Any]):
        options['token'] = self.token


class UserPassAuth(Auth):
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password

    def add_authorization_options(self, options: Dict[str, Any]):
        options['login_id'] = self.user
        options['password'] = self.password
