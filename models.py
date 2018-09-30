import peewee as pw
import datetime

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


def migrate_db():
    with db:
        db.create_tables([Chat])
