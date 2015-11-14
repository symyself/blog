#encoding: utf-8

from werkzeug import generate_password_hash,check_password_hash
from datetime import datetime
from . import db

class user(db.Model):
    __tablename__ = 'blog_user'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    email   = db.Column(db.String(32))
    register_date = db.Column(db.DateTime)

    ##def __init__(self,username,password,email):
    ##    self.username = username
    ##    self.password = password
    ##    self.email  = email
    ##    self.register_date = datetime.now()

    def __repr__(self):
        return '<%s %r>' %(self.username,self.register_date)

    @property
    def password(self):
        raise AttributeError( 'password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
