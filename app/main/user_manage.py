# encoding:utf-8
from first_flask import app
from flask import request, render_template,session
from flask import make_response
from flask import redirect
from flask import abort, flash, url_for
from first_flask.identify_code import identify as image
from first_flask.user import login as user_login
from first_flask.my_forms import user_forms
from first_flask.models import user_manage

@app.route('/')
def home():
    '''
    home
    '''
    return render_template('base.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    register
    '''
    reg_form = user_forms.register_form(request.form)
    if request.method == 'POST' and reg_form.validate():
        flash('thanks for registering')
        print 'register:%s %s %s' %(request.form.get('username'),request.form.get('password'),request.form.get('email'))
        try:
            new_user = user_manage.users(request.form.get('username'),request.form.get('password'),request.form.get('email'))
            user_manage.db.session.add(new_user)
            user_manage.db.session.commit()
        except Exception ,e:
            print e
            return 'register error!!!'
        return redirect(url_for('login'))
    else:
        return render_template('register2.html', form=reg_form)


@app.route('/login', methods=['GET', 'POST'])
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
        login_result = user_login.login_check()
        try:
            return render_template("welcome.html", password_right=login_result)
        except Exception , e:
            print e
            return 'welcome.html error!!!'
    else:
        print 'some error!!!'
        return redirect(url_for('return400'))


@app.route('/logout')
def logout():
    '''
    logout
    '''
    print '-------------------logout'
    session['login'] = False
    return redirect(url_for('home'))
    #return render_template("base.html")


@app.route('/identify')
def identify():
    '''
    验证码图片
    '''
    #ca = identify.verify_img(request, 300, 60)
    #if session['answer'] != None:
    if 'answer' in session:
        print 'old answer:%s' %session['answer']
        session.pop('answer',None)
    ca = image.verify_img(request, 150, 30)
    print 'set verify code answer:%s' %session['answer']
    return ca.display()


if __name__ == '__main__':
    #app.secret_key = 'super secret key'
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=1024, debug=True)
