# encoding:utf-8
from flask import Flask
from flask import request, render_template,session
from flask import make_response
from flask import redirect
from flask import abort, flash, url_for
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
mail=Mail()

'''
LoginManager 对象的 session_protection 属性可以设为 None、 'basic' 或 'strong' ，以提
供不同的安全等级防止用户会话遭篡改。 设为 'strong' 时， Flask-Login 会记录客户端 IP
地址和浏览器的用户代理信息， 如果发现异动就登出用户。 login_view 属性设置登录页面
的端点。回忆一下，登录路由在蓝本中定义，因此要在前面加上蓝本的名字。
'''
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

'''
Flask-PageDown 扩展定义了一个 PageDownField 类，这个类和 WTForms 中的 TextAreaField
接口一致。使用 PageDownField 字段之前，先要初始化扩展
'''
pagedown=PageDown()

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object( config[config_name] )
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app( app )
    pagedown.init_app( app )

    # 附加路由和自定义的错误页面 (???)
    # 注册蓝本
    from .auth import auth as auth_blueprint
    from .main import main as main_blueprint
    from .api_1_0 import api as api_1_0_blueprint

    app.register_blueprint( main_blueprint)
    app.register_blueprint( auth_blueprint,url_prefix='/auth' )
    app.register_blueprint( api_1_0_blueprint,url_prefix='/api/v1.0' )

    return app

if __name__ == '__main__':
    t=config['test']()
    print type(t)
    print t.SQLALCHEMY_DATABASE_URI
