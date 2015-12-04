# coding: utf-8
from flask import render_template,flash,abort,redirect,url_for
from flask.ext.login import current_user,login_required
from . import main
from ..models import Permission,User
from ..decorators import admin_required,permission_required
from ..my_forms import user_forms
from .. import db

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

@main.route( '/user/<name>' )
@login_required
def user( name ):
    '''
    用户信息
    '''
    u = User.query.filter_by( username = name ).first()
    if u is None:
        abort( 404 )
    else:
        return render_template( 'user.html',user=u)

@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    ''' 修改location about'''
    form = user_forms.edit_profile_form()
    if not form.is_submitted():
        # 初始显示表单的时候 将当前用户的profile信息显示出来 以便修改
        form.location.data = current_user.location
        form.about.data = current_user.about
    if form.validate_on_submit():
        current_user.location = form.location.data
        current_user.about = form.about.data
        db.session.add( current_user )
        db.session.commit()
        flash('your frofile is changed!')
        return redirect(url_for('main.user',name=current_user.username))
    else:
        return render_template("edit_profile.html", form=form)

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
