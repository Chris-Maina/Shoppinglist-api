""" /instance/config """
import os


class Config(object):
    """Parent class configurations"""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')  # hardworkpaysbychris
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:chris@localhost:5432/shop_api"


class DevelopmentConfig(Config):
    """Development configs"""
    DEBUG = True


class TestingConfig(Config):
    """Testing configs"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:chris@localhost:5432/test_shop_api'
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
