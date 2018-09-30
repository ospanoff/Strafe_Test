import logging

from flask import Flask

from models import migrate_db

logging.basicConfig(filename='strafe.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# noinspection PyUnresolvedReferences
import views  # for flusk to see views


@app.cli.command()
def migrate():
    migrate_db()
