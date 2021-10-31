from flask import Flask
import threading
import time
# from db.setup import con
from logger.parsers import make_actisense_from_test_dat, canboat_convert
import json
import os


def thread_function(name):
    print("Thread %s: starting", name)
    time.sleep(15)
    print("Thread %s: finishing", name)


app = Flask(__name__)


@app.route("/")
def index():
    return "Hello World!"


@app.route("/start_log")
def start_log():
    print('starting to log')

    # x = threading.Thread(target=thread_function, args=('some_thread',))
    # x.start()

    canboat_convert()

    return "file written"
