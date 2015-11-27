#encoding: utf-8
from werkzeug import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from flask.ext.login import UserMixin
from . import db, login_manager

class Role( db.Model ):
    #__tablename__ = current_app.config['TABLE_PREFIX']+'role'
    __tablename__ = 'blog_role'
    id = db.Column( db.Integer ,primary_key=True)
    rolename = db.Column ( db.String(32),unique=True )
    users = db.relationship('User',backref='role',lazy='dynamic')

    def __repr__(self):
        return '<Role %r>'%self.rolename

class User(UserMixin,db.Model):
    #__tablename__ = current_app.config['TABLE_PREFIX']+'user'
    __tablename__ = 'blog_user'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    email   = db.Column(db.String(32),unique=True)
    role_id = db.Column( db.Integer , db.ForeignKey( 'blog_role.id'))
    register_date = db.Column(db.DateTime)
    last_login_date = db.Column(db.DateTime)
    #注册后需要邮件确认
    confirmed =  db.Column( db.Boolean , default=False )

    def __init__(self,username,password,email):
        self.username = username
        self.password = password
        self.email  = email
        self.register_date = datetime.now()

    def __repr__(self):
        return '<User %s %r>' %(self.username,self.register_date)

    @property
    def password(self):
        raise AttributeError( 'password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def generate_confirmation_token( self,expiration=3600):
        s = Serializer( current_app.config['SECRET_KEY'],expiration )
        return s.dumps( {'confirm':self.id} )

    def confirm( self,token):
        s = Serializer( current_app.config['SECRET_KEY'])
        try:
            data=s.loads( token )
        except :
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add( self )
        return True


'''
Flask-Login 要求程序实现一个回调函数，使用指定的标识符加载用户
加载用户的回调函数接收以 Unicode 字符串形式表示的用户标识符。如果能找到用户，这
个函数必须返回用户对象；否则应该返回 None。
'''
@login_manager.user_loader
def load_user( user_id):
    return User.query.get( int( user_id) )
