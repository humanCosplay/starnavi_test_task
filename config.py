import logging
import os

logger = logging.getLogger(__name__)

class BaseConfiguration(object):
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/db.sqlite"
    SECRET_KEY = ""
    ENCRYPTION_KEY = ""


class DevelopmentConfig(BaseConfiguration):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BaseConfiguration.BASE_DIR}/db.sqlite"

    HOST = "localhost"
    PORT = "5000"
    SECRET_KEY = "test"
    ENCRYPTION_KEY = "test"

    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASK_ENV = 'development'

    # service code used for data blocking
    DATA_BLOCKING_CODE = "FTRS Data Blocking"


class ProductionConfiguration(BaseConfiguration):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = "production"
