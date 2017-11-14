""" /instance/config """
import os


class Config(object):
    """Parent class configurations"""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('DEFAULT_SENDER')
    APP_URL = os.getenv('APP_URL')


class DevelopmentConfig(Config):
    """Development configs"""
    DEBUG = True


class TestingConfig(Config):
    """Testing configs"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:chris@localhost:5432/test_shop_api"
    DEBUG = True


class StagingConfig(Config):
    """"Staging env configs"""
    DEBUG = True


class ProductionConfig(Config):
    """Productions env configs"""
    DEBUG = False
    TESTING = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}
