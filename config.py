import os
basedir = os.path.abspath( os.path.dirname( __file__ ))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super secret key'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SUBJECT_PREFIX = '[enjoy01]'
    MAIL_SENDER         = 'Admin <symyself@163.com>'
    ADMIN               = os.environ.get('FLASK_ADMIN') or 'songy'
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'symyself@163.com'
    MAIL_PASSWROD = 'MYPASSWROD'
    SQLALCHEMY_DATABASE_URI = 'mysql://flask:flask@127.0.0.1/flask'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://flask:flask@127.0.0.1/flask'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://flask:flask@127.0.0.1/flask'


config = {
    'dev' : DevelopmentConfig,
    'test'   : TestingConfig,
    'product': ProductionConfig,
    'default'   : DevelopmentConfig
}

if __name__ == '__main__':
    print __file__
    print os.path.dirname( __file__ )
    print basedir
