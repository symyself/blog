# encoding:utf-8
from first_flask import app
from flask import request, render_template
from flask import make_response
from flask import redirect
from flask import abort

#URL 变量规则

@app.route('/user/<username>/age/<int:age>')
def hello_world(username, age):
    user_agent = request.headers.get('User-Agent')
    return '%s %d years old!\n your browser is:%s' % (username, age, user_agent)


@app.route('/return400')
def return400():
    return '<h1>400 bad page....</h1>', 400


@app.route('/makeresponse')
def makeresponse():
    new_response = make_response('from flask import make_response')
    return new_response


@app.route('/redirect_to/<website>')
def redirect_to_website(website):
    if website == 'qq.com':
        abort(404)
    website_str = 'http://%s' %website
    return redirect(website_str)


@app.route('/hello/<name>')
def hello_user(name):
    return render_template('hello_user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
 return render_template('404.html'), 404

