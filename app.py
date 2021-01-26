import time
import os
import logging
from logging.handlers import RotatingFileHandler
from flask.logging import default_handler

import redis
from flask import Flask


app = Flask(__name__)
app.logger.removeHandler(default_handler)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
        handlers=[RotatingFileHandler(os.path.expandvars('/log/log') + '.log',
                                      maxBytes=100000, backupCount=10)],
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt='%Y-%m-%dT%H:%M:%S')


cache = redis.Redis(host='redis', port=6379)


def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    logging.debug(count)
    return 'docker-compose is working... I have been seen {} times.\n'.format(count)
