import os
from datetime import timedelta


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ALLOWED_EXTENSIONS = {'png', 'jpg'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    JWT_ERROR_MESSAGE_KEY = "message"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)


class ProductionConfig(Config):
    JWT_SECRET_KEY = os.environ['SECRET_KEY']
    # replace url prefix "postgres" with "postgresql" as SQLALCHEMY has dropped support for "postgres" (for heroku)
    # see https://stackoverflow.com/a/64698899/10272966
    # see https://stackoverflow.com/a/66787229/10272966
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'].replace(
        '://', 'ql://', 1) if os.environ['DATABASE_URL'].startswith('postgres://') else os.environ['DATABASE_URL']
