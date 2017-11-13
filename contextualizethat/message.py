from abc import ABC, abstractmethod
from typing import Iterable, List, Dict, Any, Optional

import time
from mattermostdriver import Driver
from mattermostdriver.endpoints.posts import Posts

from . import config


class Message:
    def __init__(self, msg_id: str, user: str, text: str, time: float):
        self.msg_id = msg_id
        self.user = user
        self.text = text
        self.time = time


class MessageTransport(ABC):
    @abstractmethod
    def provide_messages(self, channel: str, last_message: Optional[Message]) -> Iterable[Message]:
        raise NotImplementedError()

    @abstractmethod
    def send_message(self, channel_id: str, text: str):
        raise NotImplementedError()


class MattermostMessageTransport(MessageTransport):
    _PER_PAGE = 60

    def __init__(self):
        self._driver = Driver({
            'url': config.url,
            'token': config.token
        })
        self._driver.login()

    def provide_messages(self, channel: str, last_message: Optional[Message]) -> Iterable[Message]:
        api_posts: Posts = self._driver.posts
        page_idx = 0
        posts: List[Message] = []
        need_more = True
        while need_more:
            params = dict(page=page_idx, per_page=MattermostMessageTransport._PER_PAGE)
            if last_message is None:
                # get since a couple seconds ago?
                # we're basically waiting here...
                params['since'] = int(time.time() * 1000) - 2000
            else:
                params['after'] = last_message.msg_id

            data = api_posts.get_posts_for_channel(channel_id=channel, params=params)
            post_order = data['order']
            post_dict = data['posts']
            if len(post_order) < MattermostMessageTransport._PER_PAGE:
                need_more = False
            posts += MattermostMessageTransport._msg_from_api(post_order, post_dict)
        return posts

    @staticmethod
    def _msg_from_api(post_order: List[str], post_dict: Dict[str, Any]) -> Iterable[Message]:
        def transform_order(msg_id: str) -> Optional[Message]:
            assert msg_id in post_dict, "WTF?"
            post: Dict[str, Any] = post_dict[msg_id]
            if 'message' not in post:
                # I think this is ok, but it's not a message!
                return None
            return Message(msg_id, post['user_id'], post['message'], post['create_at'])

        return list(filter(None, map(transform_order, post_order)))

    def send_message(self, channel_id: str, text: str):
        api_posts: Posts = self._driver.posts
        api_posts.create_post(options=dict(
            channel_id=channel_id,
            message=text
        ))
