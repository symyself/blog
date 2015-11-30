# coding: utf-8
from flask import request, render_template,session,g
from flask import make_response
from flask import redirect
from flask import abort, flash, url_for
from flask.ext.login import login_required,logout_user,login_user,current_user
from ..my_forms import user_forms
from ..models import User as user
from ..email import send_email
from .. import db
from . import auth

@auth.route('/')
def base():
    return render_template( 'base.html' )


'''
对蓝本来说， before_request 钩子只能应用到属于蓝本的请求上。若想在
蓝本中使用针对程序全局请求的钩子， 必须使用 before_app_request 修饰器
'''
@auth.before_app_request
def before_request():
    print 'request.endpoint:',request.endpoint

    # 未进行邮件确认的账号，只能访问以下路由
    allow_points= [ 'auth.logout' ,
            'auth.login' ,
            'auth.identify' ,
            'auth.confirm' ,
            'auth.unconfirmed',
            'auth.register',
            'auth.resend_confirm_email',
            'static',
            'bootstrap.static' ]

    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.endpoint not in allow_points:
        return redirect( url_for( 'auth.unconfirmed'))

@auth.route( '/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect( url_for ('main.base'))
    return render_template('unconfirmed.html')

@auth.route('/resend_confirm_email')
@login_required
def resend_confirm_email():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account(resend)',
            'auth/email/confirm', user=current_user,token=token)
    flash('A new confirmation email has been sent to your email.')
    return redirect(url_for('main.base'))


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
    if not verify_code_right():
        return False

    user_for_login=user.query.filter_by( username=request.form.get('username')).first()
    if not user_for_login:
        g.error_msg=u'用户不存在'
        return False
    if password_right( user_for_login) :
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
    #login_form = user_forms.login_form(request.form)
    #if login_form.validate():
    if not current_user.is_anonymous:
        return render_template('info.html',info = ' allready logged in !!!')
    login_form = user_forms.login_form()
    if login_form.validate_on_submit():
        login_result = login_check()
        try:
            if request.args.get('next') and login_result is True:
                return redirect(request.args.get('next'))
            else:
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
    if current_user.is_authenticated:
        logout_user()
        flash('you have logged out,bye bye!!!')
        return redirect(url_for('auth.base'))
    else:
        return render_template('info.html',info = 'Error:Can\'t logout before login')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    '''
    register
    '''
    ##reg_form = user_forms.register_form(request.form)
    ##if request.method == 'POST' and reg_form.validate():
    if not current_user.is_anonymous:
        return render_template('info.html',info = ' allready logged in !!!can\'t reigister ')

    reg_form = user_forms.register_form()
    if reg_form.validate_on_submit():
        flash('thanks for registering')
        #print 'register:%s %s %s' %(request.form.get('username'),request.form.get('password'),request.form.get('email'))
        try:
            new_user = user(request.form.get('username'),
                    request.form.get('password'),
                    request.form.get('email'))
            db.session.add(new_user)
            '''
            即便通过配置，程序已经可以在请求末尾自动提交数据库变化，这里也要添加
            db.session.commit() 调用。问题在于，提交数据库之后才能赋予新用户 id 值，而确认令
            牌需要用到 id，所以不能延后提交。
            '''
            db.session.commit()
            token = new_user.generate_confirmation_token()
        except Exception ,e:
            print e
            return 'register error!!!'
        send_email(new_user.email, 'Confirm Your Account',
                               'auth/email/confirm', user=new_user,token=token)
        flash('A new confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    else:
        return render_template('register2.html', form=reg_form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    '''
    confirm account atfer register
    '''
    if current_user.confirmed:
        #return redirect(url_for('main.base'))
        return render_template('info.html',info = '此验证地址已失效!')
    if current_user.confirm( token ):
        flash('you have confirmed you account,Thanks!!')
    else:
        flash('the confirmation is invalid or has expired')
    return redirect(url_for('main.base'))



'''
为了保护路由只让认证用户访问， Flask-Login 提供了一个 login_required 修饰器。
如果未认证的用户访问这个路由， Flask-Login 会拦截请求，把用户发往登录页面。
'''
@auth.route('/secret')
@login_required
def secret():
    return render_template('info.html',info = ' this is secret page,')

@auth.route('/userinfo')
@login_required
def userinfo():
    return render_template('auth/userinfo.html')

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = user_forms.change_password_form()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.commit()
            return render_template('info.html',info = 'Your password chenged successfully!')
        else:
            return render_template('info.html',info = 'Error,old password is not correct!!!')
    else:
        return render_template('auth/change_password.html',form=form)

@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect( url_for( 'main.base'))
    form = user_forms.reset_password_email_form()
    if form.validate_on_submit():
        reset_user=user.query.filter_by(email=form.email.data).first()
        if reset_user is not None:
            token= reset_user.reset_password_token()
            send_email(reset_user.email, 'RESET YOUR PASSWORD',
                    'auth/email/reset_password', user=reset_user,token=token)
            flash('A email has been sent to your email.')
            return redirect( url_for( 'main.base'))
        else:
            return render_template('info.html',info = 'Error, email '+form.email.data+'not register!')
    else:
        return render_template('auth/reset_password.html',form=form)


@auth.route('/reset_password/<token>/<mail>', methods=['GET', 'POST'])
def reset_password(token,mail):
    if not current_user.is_anonymous:
        return redirect( url_for( 'main.base'))
    form = user_forms.reset_password_form()
    reset_user=user.query.filter_by(email=mail).first()
    if reset_user is None or reset_user.check_reset_password_token(token) is False:
        return render_template('info.html',info = 'Error,无效的连接!!!')
    if form.validate_on_submit():
        if reset_user.reset_password(form.new_password.data):
            return render_template('info.html',info = 'Your password chenged successfully!')
        else:
            return render_template('info.html',info = 'Error,while changing password!!!')
    else:
        return render_template('auth/reset_password.html',form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = user_forms.change_email_form()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            token = current_user.change_email_token(new_email=form.new_email.data)
            send_email( form.new_email.data,'CHANGE YOUR EMAIL',
                    'auth/email/change_email',user=current_user,token=token)
            flash('A email has been sent to your new email addr:'+form.new_email.data)
            return redirect( url_for( 'main.base'))
        else:
            return render_template('info.html',info = 'Error, password Error')
    else:
        return render_template('auth/change_email.html',form=form)

@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email( token ):
        flash('change email succeed!!')
    else:
        flash('the link is invalid or has expired')
    return redirect(url_for('auth.userinfo'))
    
