# encoding:utf-8
from flask import Flask
from flask import request, render_template,session
from flask import make_response
from flask import redirect
from flask import abort, flash, url_for
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object( config[config_name] )
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)

    # 附加路由和自定义的错误页面 (???)
    # 注册蓝本
    from .auth import auth as auth_blueprint
    app.register_blueprint( auth_blueprint,url_prefix='/auth' )
    
    return app

if __name__ == '__main__':
    t=config['test']()
    print type(t)
    print t.SQLALCHEMY_DATABASE_URI
