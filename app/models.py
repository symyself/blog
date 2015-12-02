#encoding: utf-8
from werkzeug import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from flask.ext.login import UserMixin,AnonymousUserMixin
from . import db, login_manager

class Permission():
    FOLLOW=0x01 #可关注别人
    COMMENT=0x02    #可评论别人的文章
    WRITE_ARTICLES=0x04 #可原创文章
    MODERATE_COMMENTS=0x08 #可管理不当评论
    ADMINISTER=0x80 #管理员

class Role( db.Model ):
    #__tablename__ = current_app.config['TABLE_PREFIX']+'role'
    __tablename__ = 'blog_role'
    id = db.Column( db.Integer ,primary_key=True)
    rolename = db.Column ( db.String(32),unique=True )

    ##是否为新注册用户的默认角色
    default = db.Column ( db.Boolean , default=False ,index=True)

    ##二进制 一个位置1 表示具有某种权限
    permissions = db.Column( db.Integer )

    users = db.relationship('User',backref='role',lazy='dynamic')

    def __repr__(self):
        return '<Role %r>'%self.rolename

    @staticmethod
    def insert_roles():
        user_permission = Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES
        moderator_permission = user_permission | Permission.MODERATE_COMMENTS
        administer_permission = 0xff #所有权限
        roles={
                'User':(user_permission,True),
                'Moderator':(moderator_permission,False),
                'Administrator':(administer_permission,False),
                }
        for rolename in roles.keys():
            role = Role.query.filter_by( rolename = rolename ).first()
            if role is None:
                role = Role( rolename=rolename )
            role.permissions = roles[rolename][0]
            role.default = roles[rolename][1]
            db.session.add( role)
        db.session.commit()

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

    def __init__(self,username,password,email,**kwargs):
        super( User,self).__init__( **kwargs )
        self.username = username
        self.password = password
        self.email  = email
        self.register_date = datetime.now()
        #为新用户定义角色
        if self.email == current_app.config['ADMIN_EMAIL']:
            self.role = Role.query.filter_by( rolename = 'Administrator' ).first()
        else:
            self.role = Role.query.filter_by( default = True ).first()

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

    def generate_reset_password_token( self,expiration=1800):
        s = Serializer( current_app.config['SECRET_KEY'],expiration )
        return s.dumps( {'name':self.username} )

    def generage_change_email_token( self,new_email,expiration=1800):
        s = Serializer( current_app.config['SECRET_KEY'],expiration )
        return s.dumps( {'name':self.username,'new_email':new_email} )

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

    def reset_password( self,new_password):
        try:
            self.password = new_password
            db.session.add( self )
        except :
            return False
        return True

    def change_email( self,token):
        s = Serializer( current_app.config['SECRET_KEY'])
        try:
            data=s.loads( token )
        except :
            return False
        if data.get('name') != self.username or data.get('new_email') is None:
            return False
        self.email = data.get('new_email')
        db.session.add( self )
        return True

    def check_permission(self,permissions):
        '''
        check user has permissions or not
        '''
        return self.role is not None and ((self.role.permissions & permissions ) == permissions )

    def is_administor(self):
        return self.check_permission( Permission.ADMINISTER )


    @staticmethod
    def get_user_from_token( token):
        s = Serializer( current_app.config['SECRET_KEY'])
        try:
            data=s.loads( token )
        except :
            return None
        username=data.get('name')
        if username is None:
            return None
        user = User.query.filter_by( username=username ).first()
        return user

'''
出于一致性考虑，我们还定义了 AnonymousUser 类，并实现了 check_permission() 方法和
is_administrator() 方法。这个对象继承自 Flask-Login 中的 AnonymousUserMixin
类，并将其设为用户未登录时 current_user 的值。这样程序不用先检查用户是否登录，就能自由调用
current_user.check_permission() 和 current_user.is_administrator()。
'''
class AnonymousUser(AnonymousUserMixin):
    def check_permission(self,permissions):
        return False
    def is_administor(self):
        return False
login_manager.anonymous_user = AnonymousUser

'''
Flask-Login 要求程序实现一个回调函数，使用指定的标识符加载用户
加载用户的回调函数接收以 Unicode 字符串形式表示的用户标识符。如果能找到用户，这
个函数必须返回用户对象；否则应该返回 None。
'''
@login_manager.user_loader
def load_user( user_id):
    return User.query.get( int( user_id) )

