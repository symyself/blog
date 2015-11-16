# coding: utf-8
from flask import request, render_template,session
from flask import make_response
from flask import redirect
from flask import abort, flash, url_for
from ..my_forms import user_forms
from ..models import user
from .. import db
from . import auth

@auth.route('/')
def index():
    return render_template( 'base.html' )

@auth.route('/test')
def test():
    return 'test ok'

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
        '''
        sy=user.query.filter_by( username='songy').first()
        sy.verify_password('songy')
        '''
        login_result = True
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
    return redirect(url_for('home'))
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
