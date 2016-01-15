# encoding: utf-8
from flask.ext.wtf import Form
from wtforms import BooleanField, PasswordField, StringField, SubmitField,TextAreaField
from wtforms.validators import Required,DataRequired,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User
from flask import session
from flask.ext.login import current_user
from flask.ext.pagedown.fields import PageDownField

'''
from wtforms import Form, BooleanField, TextField, PasswordField, validators, StringField, SubmitField

class register_form(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('email', [validators.Length(min=6, max=35)])
    password = PasswordField('password', [
        validators.Required(), validators.EqualTo('confirm', message='password must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.required()])
'''

class register_form(Form):
    username = StringField('Username',
            validators=[
                    Required() ,
                    Length(5,32,'至少5字符'),
                    Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,u'字符(开头)，数字，下划线！')])
    email = StringField('email', validators=[Required(),Length(4,32,u'邮件地址太短了！'),Email()])
    password = PasswordField('password',
                validators=[Required(),Length(4,16,u'密码太短!'), EqualTo('confirm', message=u'两次密码不一致')])
    confirm = PasswordField('Repeat Password',validators=[Required()])
    ##accept_tos = BooleanField('I accept the TOS')
    submit = SubmitField('Register')


    '''
    这个表单还有两个自定义的验证函数， 以方法的形式实现。如果表单类中定义了以
    validate_ 开头且后面跟着字段名的方法，这个方法就和常规的验证函数一起调用。本例
    分别为 email 和 username 字段定义了验证函数，确保填写的值在数据库中没出现过。自定
    义的验证函数要想表示验证失败，可以抛出 ValidationError 异常，其参数就是错误消息。
    '''
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(str(field.data)+'\n already registerd')

    def validate_email(self,field):
        if User.query.filter_by( email=field.data).first():
            raise ValidationError( str( field.data ) + '\n already registerd')

    ###def validate_accept_tos(self,field):
    ###    if field.data == False:
    ###        print 'not check'
    ###        raise ValidationError('must check accept')


class login_form(Form):
    username = StringField('Username', validators=[Required(), Length(min=5, max=32,message=u'至少5字符'),
                    Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,u'字符(开头) or 数字 or 下划线！')])
    password = PasswordField('Password', validators=[Required(),Length(4,16,u'密码太短')])
    verify_code = StringField('Verify Dode',validators= [Required()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')
    def validate_username(self,field):
        if not User.query.filter_by(username=field.data).first():
            raise ValidationError(str(field.data)+' 用户不存在!!')

    def validate_password(self,field):
        user=User.query.filter_by(username=self.username.data).first()
        if user is not None:
            if user.verify_password( field.data ) is False:
                raise ValidationError(' 密码错误!!')

    def validate_verify_code(self,field):
        user_code = field.data
        system_code = session['answer']
        if user_code != system_code:
            raise ValidationError(' 验证码错误!!')

class change_password_form(Form):
    old_password = PasswordField(u'旧密码', validators=[Required(),Length(4,16,u'密码太短')])
    new_password = PasswordField(u'新密码',
                validators=[
                    Required(),Length(4,16,u'密码太短!'),
                    EqualTo('confirm', message=u'两次密码不一致')])
    confirm = PasswordField(u'新密码',validators=[Required()])
    submit = SubmitField(u'修改')

    def validate_old_password(self,field):
        if current_user.verify_password( field.data ) is False:
            raise ValidationError(' 密码错误!!')

class reset_password_email_form(Form):
    email = StringField('your email for reset password',
                validators=[Required(),Length(4,32,u'邮件地址太短了！'),Email(message=u'不太像一个邮件地址额--')])
    submit = SubmitField(u'确定')
    def validate_email(self,field):
        if not User.query.filter_by( email=field.data).first():
            raise ValidationError( str( field.data ) + '\n 还木有注册呢，快去注册吧！')

class reset_password_form(Form):
    new_password = PasswordField(u'新密码',
                validators=[
                    Required(),
                    Length(4,16,u'密码太短!'),
                    EqualTo('confirm',message=u'两次密码不一致')
                    ]
                )
    confirm = PasswordField(u'新密码',validators=[Required()])
    submit = SubmitField(u'确定')

class change_email_form(Form):
    password = PasswordField(u'密码', validators=[Required(),Length(4,16,u'密码太短')])
    new_email = StringField(u'新邮件地址',
                validators=[Required(),Length(4,32,u'邮件地址太短了！'),Email(message=u'不太像一个邮件地址额--')])
    submit = SubmitField(u'确定')
    def validate_password(self,field):
        if current_user.verify_password( field.data ) is False:
            raise ValidationError(' 密码错误!!')

    def validate_new_email(self,field):
        if User.query.filter_by( email=field.data).first():
            raise ValidationError( str( field.data ) + '\n 已经注册了！换一个吧！')

class edit_profile_form(Form):
    location = StringField(u'坐标',validators=[Length(0,16)])
    about = TextAreaField(u'自我介绍',)
    submit = SubmitField(u'确定')
    ##def __init__(self,user,**kwargs):
    ##    self.location.data= user.location
    ##    self.about.data = user.about
    ##    super( edit_profile_form,self).__init__( **kwargs )

class post_form(Form):
    title = StringField(u'title',validators=[Required(),Length(3,128)])
    #body = TextAreaField( u'body',validators=[Required()])
    body = PageDownField( u'body',validators=[Required()])
    submit = SubmitField(u'确定')

class comment_form(Form):
    #body = TextAreaField( u'body',validators=[Required()])
    body = PageDownField( u'评论',validators=[Required()])
    submit = SubmitField(u'确定')

class new_article_form(Form):
    title = StringField(u'title',validators=[Required(),Length(3,128)])
    content = TextAreaField( u'content',validators=[Required()])
    #body = PageDownField( u'body',validators=[Required()])
    submit = SubmitField(u'确定')
