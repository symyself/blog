# coding: utf-8
from flask import request, render_template,session,g
from flask import make_response
from flask import redirect
from flask import abort, flash, url_for
from flask.ext.login import login_required,logout_user,login_user
from ..my_forms import user_forms
from ..models import user
from ..email import send_email
from .. import db
from . import auth

@auth.route('/')
def base():
    return render_template( 'base.html' )

def password_right( user_for_login):
    if not user_for_login.verify_password(request.form.get('password')):
        g.error_msg = u'密码错误'
        return False
    else:
        return True


def verify_code_right():
    user_code = request.form.get('verify_code')
    system_code = session['answer']
    if user_code == system_code:
        return True
    else:
        g.error_msg = u'验证码错误'
        return False

def login_check():
    user_for_login=user.query.filter_by( username=request.form.get('username')).first()
    if not user_for_login:
        g.error_msg=u'用户不存在'
        return False
    if password_right( user_for_login) and verify_code_right():
        ##session['username'] = user_for_login.username
        ##session['login'] = True
        '''
        login_user() 函数的参数是要登录的用户，以及可选的“记住我”布
        尔值，“记住我”也在表单中填写。如果值为 False，那么关闭浏览器后用户会话就过期
        了，所以下次用户访问时要重新登录。 如果值为 True，那么会在用户浏览器中写入一个长
        期有效的 cookie，使用这个 cookie 可以复现用户会话。
        '''
        login_user(user_for_login , request.form.get('remember_me'))
        return True
    else:
        return False

@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''
    login
    '''
    print 'debug-------------login----------debug'
    #login_form = user_forms.login_form(request.form)
    #if login_form.validate():
    login_form = user_forms.login_form()
    if login_form.validate_on_submit():
        login_result = login_check()
        try:
            if request.args.get('next') and login_result:
                print 'login ok next-->'
                print request.args.get('next')
                print 'request.args',request.args
                print 'request',request
                return redirect(request.args.get('next'))
            else:
                print 'request.args',request.args
                print 'request',request
                return render_template("welcome.html", password_right=login_result)
        except Exception , e:
            print e
            return 'welcome.html error!!!'
    else:
        #return redirect(request.args.get('next') or url_for('main.index'))
        return render_template("login2.html", form=login_form)


@auth.route('/logout')
def logout():
    '''
    logout
    '''
    print '-------------------logout'
    #session['login'] = False
    #session.pop('username',None)
    logout_user()
    return redirect(url_for('auth.base'))
    #return render_template("base.html")


@auth.route('/register', methods=['GET', 'POST'])
def register():
    '''
    register
    '''
    reg_form = user_forms.register_form(request.form)
    if request.method == 'POST' and reg_form.validate():
        flash('thanks for registering')
        #print 'register:%s %s %s' %(request.form.get('username'),request.form.get('password'),request.form.get('email'))
        try:
            new_user = user(request.form.get('username'),
                    request.form.get('password'),
                    request.form.get('email'))
            db.session.add(new_user)
            db.session.commit()
        except Exception ,e:
            print e
            return 'register error!!!'
        send_email(new_user.email, 'Confirm Your Account',
                               'auth/email/confirm', user=new_user)
        flash('A new confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    else:
        return render_template('register2.html', form=reg_form)

'''
为了保护路由只让认证用户访问， Flask-Login 提供了一个 login_required 修饰器。
如果未认证的用户访问这个路由， Flask-Login 会拦截请求，把用户发往登录页面。
'''
@auth.route('/secret')
@login_required
def secret():
    return render_template('info.html',info = ' this is secret page,')
