# coding: utf-8
from flask import render_template,flash
from flask.ext.login import current_user,login_required
from . import main
from ..models import Permission
from ..decorators import admin_required,permission_required

@main.route('/')
def base():
    #flash('weclome')
    return render_template( 'base.html' )

@main.route('/admin')
@login_required
@admin_required
def admin():
    return render_template('info.html',info = 'hello admin')

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderator():
    return render_template('info.html',info = 'hello moderator')

@main.app_errorhandler(403)
def permission_failed(e):
    return render_template('info.html',info = 'permission failed'),403


'''
在模板中可能也需要检查权限，所以 Permission 类为所有位定义了常量以便于获取。为了
避免每次调用 render_template() 时都多添加一个模板参数，可以使用上下文处理器。上
下文处理器能让变量在所有模板中全局可访问。
'''
@main.app_context_processor
def inject_permissions():
     return dict(Permission=Permission)
