# coding: utf-8
from flask import request, render_template,session,g
from flask import make_response
from flask import redirect
from flask import abort, flash, url_for
from ..my_forms import user_forms
from ..models import user
from .. import db
from . import auth

@auth.route('/')
def base():
    return render_template( 'base.html' )

def password_right( login_user):
    if not login_user.verify_password(request.form.get('password')):
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
    login_user=user.query.filter_by( username=request.form.get('username')).first()
    if not login_user:
        g.error_msg=u'用户不存在'
        return False
    if password_right( login_user) and verify_code_right():
        session['username'] = login_user.username
        session['login'] = True
        return True
    else:
        return False

@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''
    login
    '''
    print 'debug-------------login----------debug'
    login_form = user_forms.login_form(request.form)
    if request.method == 'GET' or request.method == 'HEAD':
        print 'GET/HEAD'
        return render_template("login2.html", form=login_form)
    elif login_form.validate():
        #login_result = user_login.login_check()
        login_result = login_check()
        try:
            return render_template("welcome.html", password_right=login_result)
        except Exception , e:
            print e
            return 'welcome.html error!!!'
    else:
        print 'some error!!!'
        return redirect(url_for('return400'))


@auth.route('/logout')
def logout():
    '''
    logout
    '''
    print '-------------------logout'
    session['login'] = False
    session.pop('username',None)
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
        print 'register:%s %s %s' %(request.form.get('username'),request.form.get('password'),request.form.get('email'))
        try:
            new_user = user(request.form.get('username'),
                    request.form.get('password'),
                    request.form.get('email'))
            db.session.add(new_user)
            db.session.commit()
        except Exception ,e:
            print e
            return 'register error!!!'
        return redirect(url_for('auth.login'))
    else:
        return render_template('register2.html', form=reg_form)
