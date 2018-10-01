import logging
import threading
import time

from models import Chat
from settings import LOGGING_LEVEL
from settings import TRACK_SLEEP_PERIOD, API_VERSION
from twitch_api import TwitchChat

log = logging.getLogger(__name__)
log.setLevel(LOGGING_LEVEL)


class ChatTracker(threading.Thread):
    def __init__(self, channel_name):
        threading.Thread.__init__(self)
        self.shutdown_flag = threading.Event()
        self.channel_name = channel_name

    def run(self):
        log.info('Started tracking {}'.format(self.channel_name))

        chat = TwitchChat()
        chat.join_channel(self.channel_name)

        while not self.shutdown_flag.is_set():
            messages = chat.get_messages()
            if messages:
                Chat.save_messages(messages)

            time.sleep(TRACK_SLEEP_PERIOD)

        chat.close_connection()
        log.info('Stopped tracking {}'.format(self.channel_name))


def api_prefix(path):
    return '/api/v{}/{}'.format(API_VERSION, path.lstrip('/'))
