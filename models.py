import datetime

import peewee as pw

from settings import DATABASE

db = pw.SqliteDatabase(DATABASE)


class Chat(pw.Model):
    name = pw.CharField()
    time_added = pw.DateTimeField(default=datetime.datetime.now)
    message = pw.TextField()
    sender = pw.CharField()

    class Meta:
        database = db

    @staticmethod
    def save_messages(messages):
        """
        Saves a message into db
        :param messages: list of tuples of sender, chat name and message
        :return:
        """
        with db.atomic():
            Chat.insert_many(messages, fields=[Chat.sender, Chat.name, Chat.message]).execute()

    @staticmethod
    def get_messages(channel, window=10, limit=100):
        """
        Gets messages of the channel that starts from (now - period minutes) time
        :param channel: channel for getting messages
        :param window: period in minutes
        :param limit: limit messages amount
        :return: list of messages
        """
        dt_start = datetime.datetime.now() - datetime.timedelta(minutes=window)
        messages = [
            rec.message for rec in Chat.select().where(
                (Chat.time_added >= dt_start) & (Chat.name == channel)
            ).order_by(Chat.time_added.desc()).limit(limit)
        ]

        return messages

    @staticmethod
    def get_messages_cnt(channel, window=10):
        """
        Gets number of messages of the channel that starts from (now - period minutes) time
        :param channel: channel for getting messages
        :param window: period in minutes
        :return: int, number of messages
        """
        dt_start = datetime.datetime.now() - datetime.timedelta(minutes=window)
        cnt = Chat.select().where(
            (Chat.time_added >= dt_start) & (Chat.name == channel)
        ).count()

        return cnt


def migrate_db():
    with db:
        db.create_tables([Chat])
