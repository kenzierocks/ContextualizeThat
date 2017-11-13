import random
import sys
import time
import traceback
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
    if not config.authentication:
        raise fail("No authentication method provided!")
    if config.url == 'example.com':
        raise fail("There's no Mattermost server at example.com!")

    print('> Initializing bot...')
    databases = {ch: config.database(ch) for ch in channels}
    oracles: Dict[str, ChatOracle] = {ch: ChatOracle(databases[ch]) for ch in channels}
    bot_algo = config.algo
    msg_transport = MattermostMessageTransport()
    error_policy = config.error_policy

    reply_messages = config.reply_messages

    def random_message():
        return random.choice(reply_messages)

    try:
        while True:
            try:
                for channel in channels:
                    print('#', channel)
                    ch_oracle = oracles[channel]
                    print('> Feeding messages...')
                    last_message = ch_oracle.get_latest_message()
                    messages = msg_transport.provide_messages(channel, last_message)
                    ch_oracle.feed_messages(messages)
                    print('> Running algorithms...')
                    if bot_algo.send_context_message(ch_oracle):
                        print('Sending UNO message.')
                        msg_transport.send_message(channel, random_message())
                print('> Sleeping...')
                time.sleep(10 * 60)
            except Exception as ex:
                print('> Error, sleeping:')
                traceback.print_exc()
                time.sleep(error_policy.accept_error(ex))
    finally:
        for db in databases.values():
            db.close()
