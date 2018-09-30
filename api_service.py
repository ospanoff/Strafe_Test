import time
import threading
from twitch_api import TwitchChat
from settings import TRACK_SLEEP_PERIOD, LOGGING_LEVEL
from models import Chat
import logging

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
