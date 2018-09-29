import errno
import fcntl
import logging
import os
import re
import socket
import time

from settings import TWITCH_BOT_USERNAME
from settings import TWITCH_IRC_HOST
from settings import TWITCH_IRC_OAUTH
from settings import TWITCH_IRC_PORT

RECV_BUFFER_SIZE = 2048
TWITCH_ALLOWED_CHARS = '[a-zA-Z0-9_]'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TwitchChat:
    channel_name = None

    __sock = None
    __appendix = ''

    __re_ping = re.compile(r'^PING :tmi\.twitch\.tv$')
    __re_channel = re.compile(r'^:{tac}+!{tac}+@{tac}+\.tmi\.twitch\.tv JOIN #({tac}+)$'
                              .format(tac=TWITCH_ALLOWED_CHARS))
    __re_priv_msg = re.compile(r'^:({tac}+)!{tac}+@{tac}+\.tmi\.twitch\.tv PRIVMSG #({tac}+) :(.+)$'
                               .format(tac=TWITCH_ALLOWED_CHARS))

    def __init__(self, verbose=False):
        """
        Creates connection with Twitch IRC
        :param verbose: Print more info
        """
        self.verbose = verbose
        self.__connect()

    def __connect(self):
        """
        Authorizes user on Twitch IRC. Raises error if failed
        """
        if self.__sock:
            self.close_connection()

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.__sock.connect((TWITCH_IRC_HOST, TWITCH_IRC_PORT))
        except OSError:
            log.error('Socket creation error')

        self.__send_command('PASS', TWITCH_IRC_OAUTH)
        self.__send_command('NICK', TWITCH_BOT_USERNAME)

        response = self.__sock.recv(RECV_BUFFER_SIZE).decode()
        if self.verbose:
            print(response)

        if self.__has_logged_in(response):
            fcntl.fcntl(self.__sock, fcntl.F_SETFL, os.O_NONBLOCK)
        else:
            msg = 'Wrong Oauth password'
            log.error(msg)
            raise Exception(msg)

    @staticmethod
    def __has_logged_in(response):
        return re.match(r':tmi\.twitch\.tv [0-9]{{3}} {tac}+ :Welcome, GLHF!'
                        .format(tac=TWITCH_ALLOWED_CHARS), response) is not None

    def __send_command(self, command, value=''):
        self.__sock.sendall('{} {}\r\n'.format(command, value).encode('utf-8'))

    def __flush_socket(self):
        """
        Reads the socket with an error control
        :return: string, the data from the server
        """
        try:
            return self.__sock.recv(RECV_BUFFER_SIZE).decode()
        except socket.error as e:
            error = e.args[0]
            if error == errno.EAGAIN or error == errno.EWOULDBLOCK:
                # log.info('No message in the socket')
                pass
            else:
                log.error('Socket is broken. Trying to reconnect!')
                self.__connect()
                self.join_channel(self.channel_name)

        return ''

    def __parse_record(self, record):
        """
        Parses one record from the respond. It return message information if it a message,
        responds to the server if it asks for PONG and checks if we connected to the channel
        :param record: One record in the respond
        :return: dict of (username, channel and message) if it is a message and None otherwise
        """
        channel_name = self.__re_channel.findall(record)
        priv_msg = self.__re_priv_msg.findall(record)
        # if we get PING message, we should answer PONG (happens each ~5mins)
        if self.__re_ping.match(record):
            self.__send_command('PONG')
            log.info('PONG was sent')
        # if we joined a channel
        elif channel_name:
            self.channel_name = channel_name[0]
            log.info('Connected to channel: {}'.format(self.channel_name))
        elif priv_msg:  # it is a private message
            priv_msg = priv_msg[0]
            return {
                'username': priv_msg[0],
                'channel': priv_msg[1],
                'message': priv_msg[2]
            }

    def join_channel(self, channel_name):
        self.__send_command('JOIN', '#' + channel_name)
        # joining channel is not instant, wait a sec
        time.sleep(1)

    def get_messages(self):
        messages = []
        while True:
            data = self.__flush_socket()
            if not data:
                break

            records = data.split('\r\n')
            # if buffer is overflowed, then with have unfinished message which should be the beginning of the next
            records[0] = self.__appendix + records[0]
            self.__appendix = records.pop()  # if the message fully finishes, it is an empty string

            for record in records:
                msg = self.__parse_record(record)
                if msg:
                    messages += [msg]

        if messages:
            log.info('Got {} messages'.format(len(messages)))

        return messages

    def close_connection(self):
        self.__sock.close()
