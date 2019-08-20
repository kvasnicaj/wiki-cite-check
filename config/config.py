import os


class Config(object):
    DEBUG = True
    ROW_LIMIT = 10
    SECRET_KEY = os.environ.get('SECRET_KEY')
