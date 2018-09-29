import logging
import time

from twitch_api import TwitchChat

logging.basicConfig(filename='strafe.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


if __name__ == '__main__':
    chat = TwitchChat()
    chat.join_channel('0spanoff')
    _start = time.time()
    while True:
        print(chat.get_messages())
        time.sleep(1)

        if time.time() - _start > 360:
            break

    chat.close_connection()
