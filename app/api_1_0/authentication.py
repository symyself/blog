#!/bin/env python2.7
#! -*- coding: UTF-8 -*-
from . import api
from flask.ext.httpauth import HTTPBasicAuth
from flask import g,jsonify
from ..models import User,AnonymousUser
import errors
auth = HTTPBasicAuth()


'''
在将 HTTP 基本认证的扩展进行初始化之前，我们先要创建一个 HTTPBasicAuth 类对象。
和 Flask-Login 一样， Flask-HTTPAuth 不对验证用户密令所需的步骤做任何假设，因此所
需的信息在回调函数中提供。
'''
@auth.verify_password
def verify_password(username_or_token,password):
    if username_or_token == '':
        g.current_user = AnonymousUser()
        return True

    if password == '':
        g.current_user = User.verify_auth_token( username_or_token )
        g.token_used = True
        return ( g.current_user is not None )

    user = User.query.filter_by( username = username_or_token ).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password( password )

'''
这个蓝本中的所有路由都要使用相同的方式进行保护，所以我们可以在 before_
request 处理程序中使用一次 login_required 修饰器，应用到整个蓝本
'''
@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return errors.forbidden('not confirmed')


@auth.error_handler
def auth_error():
    return errors.unauthorized('Invalid credentials')

@api.route('/posts/')
@auth.login_required
def get_posts():
    return errors.forbidden('not confirmed')

@api.route('/token/')
def get_token():
    if g.current_user.is_anonymous or g.token_used :
        return errors.unauthorized( 'Invalid cerdentials')
    return jsonify( {'token':g.current_user.generate_auth_token(expiration=600),
        'expiration':600})

