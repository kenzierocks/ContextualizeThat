import random
import sys
from typing import Dict

from . import config
from .algo import Algo
from .message import MattermostMessageTransport
from .oracle import ChatOracle


def fail(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def start():
    channels = config.channels
    if not channels:
        raise fail("No channels provided!")
    if not config.token:
        raise fail("No token provided!")
    if config.url == 'example.com':
        raise fail("There's no Mattermost server at example.com!")

    databases = {ch: config.database(ch) for ch in channels}
    oracles: Dict[str, ChatOracle] = {ch: ChatOracle(databases[ch]) for ch in channels}
    bot_algo = config.algo
    msg_transport = MattermostMessageTransport()

    reply_messages = config.reply_messages

    def random_message():
        return random.choice(reply_messages)

    try:
        while True:
            for channel in channels:
                ch_oracle = oracles[channel]
                last_message = ch_oracle.get_latest_message()
                messages = msg_transport.provide_messages(channel, last_message)
                ch_oracle.feed_messages(messages)
                if bot_algo.send_context_message(ch_oracle):
                    msg_transport.send_message(channel, random_message())

    finally:
        for db in databases.values():
            db.close()
