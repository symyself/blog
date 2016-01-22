#encoding: utf-8
from werkzeug import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,url_for
from datetime import datetime
from flask.ext.login import UserMixin,AnonymousUserMixin
from . import db, login_manager
from markdown import markdown
from exceptions import ValidationError
import bleach

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


class Post(db.Model):
    '''博客文章
    '''
    __tablename__ = 'blog_post'
    id = db.Column( db.Integer ,primary_key=True)
    title = db.Column( db.String(128),nullable=False)
    alias = db.Column( db.String(128),unique=True)
    body = db.Column( db.Text ,nullable=False)
    #将markdown格式的body转换为html存放
    body_html = db.Column( db.Text )
    create_time = db.Column( db.DateTime , default=datetime.now )
    last_change_time = db.Column( db.DateTime , default=datetime.now )
    author_id = db.Column(db.Integer,db.ForeignKey( 'blog_user.id' ))
    comments = db.relationship( 'Comment',backref='post',lazy='dynamic')

    def to_json( self ):
        '''
        把文章转换成 JSON 格式的序列化字典
        '''
        json_post={'url':url_for('api.get_post',id=self.id,_external=True),
                'title':self.title,
                'body':self.body,
                'body_html':self.body_html,
                'create_time':self.create_time,
                'last_change_time':self.last_change_time,
                'author':url_for('api.get_user',id=self.author.id,_external=True),
                'comments':url_for('api.get_post_comments',id=self.id,_external=True),
                'comments_count':self.comments.count()
                }
        return json_post

    @staticmethod
    def from_json( json_post ):
        '''
        从 JSON 格式数据创建一篇博客文章
        '''
        body = json_post.get('body')
        title = json_post.get('title')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        if title is None or title == '':
            raise ValidationError('post does not have a title')
        return Post( body=body,title=title )

    @staticmethod
    def generate_fake(count=100):
        '''
        快速添加虚拟文章
        '''
        from random import seed,choice
        import forgery_py
        seed()
        all_user_id=[ x.id for x in db.session.query(User.id).all() ]
        for i in range( count ):
            u=User.query.filter_by( id= choice( all_user_id ) ).first()
            title = forgery_py.lorem_ipsum.sentence()
            if len(title) >127:
                title=title[:128]
            p=Post(title = title,
                    body = forgery_py.lorem_ipsum.sentences(3),
                    author = u )
            db.session.add(p)
            db.session.commit()
            db.session.rollback()

    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value,output_format='html'),
            tags = allowed_tags,
            strip = True )
            )
'''
on_changed_body 函数注册在 body 字段上，是 SQLAlchemy“ set”事件的监听程序，这意
味着只要这个类实例的 body 字段设了新值，函数就会自动被调用。 on_changed_body 函数
把 body 字段中的文本渲染成 HTML 格式，结果保存在 body_html 中，自动且高效地完成
Markdown 文本到 HTML 的转换。
'''
#使用ueditor编辑器直接提交html,不再需要从markdown转换过程
#db.event.listen(Post.body,'set',Post.on_changed_body)



'''
用户关注
'''
class Follow(db.Model):
    __tablename__ = 'blog_follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('blog_user.id'),
            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('blog_user.id'),
            primary_key=True)
    follow_time = db.Column(db.DateTime, default=datetime.now)

class User(UserMixin,db.Model):
    #__tablename__ = current_app.config['TABLE_PREFIX']+'user'
    __tablename__ = 'blog_user'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    email   = db.Column(db.String(32),unique=True)
    role_id = db.Column( db.Integer , db.ForeignKey( 'blog_role.id'))
    location = db.Column( db.String(128))
    #db.String 和 db.Text 的区别在于后者不需要指定最大长度
    about = db.Column( db.Text())
    register_date = db.Column(db.DateTime,default=datetime.now)
    last_login_date = db.Column(db.DateTime,default=datetime.now)
    #注册后需要邮件确认
    confirmed =  db.Column( db.Boolean , default=False )
    head_img = db.Column( db.String(64) , default='no.jpeg')
    posts = db.relationship( 'Post',backref='author',lazy='dynamic')
    comments = db.relationship( 'Comment',backref='author',lazy='dynamic')

    #我关注的用户
    followed = db.relationship('Follow',
            foreign_keys=[Follow.follower_id],
            backref=db.backref('follower', lazy='joined'),
            lazy='dynamic',
            cascade='all, delete-orphan')
    #关注我的用户
    followers = db.relationship('Follow',
            foreign_keys=[Follow.followed_id],
            backref=db.backref('followed', lazy='joined'),
            lazy='dynamic',
            cascade='all, delete-orphan')

    def __init__(self,username,password,email,**kwargs):
        super( User,self).__init__( **kwargs )
        self.username = username
        self.password = password
        self.email  = email
        self.head_img = self.get_random_head_img()
        #self.register_date = datetime.now()
        #为新用户定义角色
        if self.email == current_app.config['ADMIN_EMAIL']:
            self.role = Role.query.filter_by( rolename = 'Administrator' ).first()
        else:
            self.role = Role.query.filter_by( default = True ).first()
        #关注自己
        #self.follow(self)
        self.followed.append( Follow( followed=self) )

    def __repr__(self):
        return '<User %s %r>' %(self.username,self.register_date)

    def to_json(self):
        '''
        把用户转换成 JSON 格式的序列化字典
        '''
        json_user={
                'url':url_for('api.get_user',id=self.id,_external=True),
                'username':self.username,
                'register_date':self.register_date,
                'last_login_date':self.last_login_date,
                'head_img':self.image_url(_external=True),
                'posts':url_for('api.get_user_posts',id=self.id,_external=True),
                'posts_count':self.posts.count(),
                'followed_posts':url_for('api.get_user_followed_posts',id=self.id,_external=True),
                }
        return json_user

    @staticmethod
    def generate_fake(count=100):
        '''
        快速添加虚拟用户
        '''
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range( count ):
            u = User( username=forgery_py.internet.user_name(),
                    password=forgery_py.lorem_ipsum.word(),
                    email=forgery_py.internet.email_address(),
                    location=forgery_py.address.city(),
                    about = forgery_py.lorem_ipsum.sentence()
                    )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

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

    def generate_auth_token( self,expiration=300):
        '''
        generate token for api auth
        '''
        s = Serializer( current_app.config['SECRET_KEY'],expiration )
        return s.dumps( {'id':self.id} )

    @staticmethod
    def verify_auth_token(token):
        '''
        verify token for api auth
        '''
        s = Serializer( current_app.config['SECRET_KEY'])
        try:
            data = s.loads( token )
        except:
            return None
        return User.query.get( data['id'] )

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

    def update_login_time( self):
        '''update login time'''
        self.last_login_date = datetime.now()
        db.session.add(self)
        db.session.commit()

    def image_url( self ,_external=False):
        '''
        return head image url for user
        '''
        img='user_head/'+self.head_img
        return url_for('static',filename=img,_external=_external)

    def get_random_head_img( self):
        '''
        get a random image file name
        '''
        from random import choice
        all_head_img=["0884eaba68735afe9f0a41675676c6d6.jpeg",
                "15c16dca753e02f88d24a8e768ab51ca.jpeg",
                "314a47601ef6514ae02c928c6c8b3baf.jpeg",
                "560317b58751214e51a617d72c72ea90.jpeg",
                "9de177c8dcf7f60baa155b2247bd1c22.jpeg",
                "c523b43d258172a002de82dd4a3d4ad2.jpeg",
                "ccdb254542bff3e0477b88b9f4a2c593.jpeg",
                "e84ee95856aa152979889dd6ee35191d.jpeg",
                "ec580cdbde25a148eaf381e6a633e1b4.jpeg"]
        return choice( all_head_img )

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

    def is_following(self, user):
        return self.followed.filter_by(
                followed_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_followed_by(self, user):
        return self.followers.filter_by(
                follower_id=user.id).first() is not None

    @property
    def followed_posts( self ):
        '''
        返回用户所有关注的人的文章
        '''
        return Post.query.join( Follow ,Follow.followed_id == Post.author_id)\
                .filter( Follow.follower_id == self.id)\
                .order_by( Post.last_change_time.desc() )

    @staticmethod
    def add_follow_self():
        '''
        所有用户自己关注自己
        '''
        for u in User.query.all():
            if not u.is_following( u ):
                u.follow( u )
                db.session.add( u )
        db.session.commit()
##class end

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


class Comment( db.Model ):
    __tablename__ = 'blog_comment'
    '''博客评论
    '''
    id = db.Column( db.Integer ,primary_key=True)
    body = db.Column( db.Text ,nullable=False)
    #将markdown格式的body转换为html存放
    body_html = db.Column( db.Text )
    create_time = db.Column( db.DateTime , default=datetime.now )
    author_id = db.Column(db.Integer,db.ForeignKey( 'blog_user.id' ))
    post_id = db.Column( db.Integer,db.ForeignKey('blog_post.id'))
    disabled =  db.Column( db.Boolean , default=False )
    audited =  db.Column( db.Boolean , default=False )

    def to_json( self ):
        '''
        '''
        json_comment={
                'url':url_for('api.get_comment',id=self.id,_external=True),
                'body':self.body,
                'body_html':self.body_html,
                'author':url_for('api.get_user',id=self.author_id,_external=True),
                'create_time'   :   self.create_time,
                }
        return json_comment

    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code',
                'em', 'i', 'strong', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value,output_format='html'),
            tags = allowed_tags,
            strip = True )
            )
'''
on_changed_body 函数注册在 body 字段上，是 SQLAlchemy“ set”事件的监听程序，这意
味着只要这个类实例的 body 字段设了新值，函数就会自动被调用。 on_changed_body 函数
把 body 字段中的文本渲染成 HTML 格式，结果保存在 body_html 中，自动且高效地完成
Markdown 文本到 HTML 的转换。
'''
db.event.listen(Comment.body,'set',Comment.on_changed_body)

