# coding: utf-8
from flask import render_template,flash,abort,redirect,url_for,request
from flask.ext.login import current_user,login_required
from . import main
from ..models import Permission,User,Post
from ..decorators import admin_required,permission_required
from ..my_forms import user_forms
from datetime import datetime
from .. import db

@main.route('/', methods=['GET', 'POST'])
def base():
    #flash('weclome')
    form = user_forms.post_form()
    if current_user.check_permission(Permission.WRITE_ARTICLES)\
            and form.validate_on_submit():
        post=Post( title=form.title.data,
                body=form.body.data,
                author=current_user._get_current_object())
        db.session.add( post )
        return redirect( url_for('.base'))
    #posts = Post.query.order_by( Post.create_time.desc()).all()
    page = request.args.get( 'page',1,type=int)
    pagination = Post.query.order_by( Post.create_time.desc()).paginate(
            page,per_page=10,error_out=False)
    posts=pagination.items
    return render_template( 'index.html' ,form=form ,posts=posts,pagination=pagination)

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
        posts = u.posts.order_by( Post.create_time.desc()).all()
        return render_template( 'user.html',user=u,posts=posts)

@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    ''' 修改location about'''
    form = user_forms.edit_profile_form()
    ###if not form.is_submitted():
    ###    # 初始显示表单的时候 将当前用户的profile信息显示出来 以便修改
    ###    form.location.data = current_user.location
    ###    form.about.data = current_user.about
    if form.validate_on_submit():
        current_user.location = form.location.data
        current_user.about = form.about.data
        db.session.add( current_user )
        db.session.commit()
        flash('your frofile is changed!')
        return redirect(url_for('main.user',name=current_user.username))
    else:
        # 初始显示表单的时候 将当前用户的profile信息显示出来 以便修改
        form.location.data = current_user.location
        form.about.data = current_user.about
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

@main.route('/get_post_<id>.html')
def get_post(id):
    post = Post.query.get_or_404(id)
    return render_template( 'post.html',posts=[post] )


@main.route("/edit_post_<id>.html",methods=['GET','POST'])
@login_required
def edit_post(id):
    form = user_forms.post_form()
    post = Post.query.get_or_404(id)
    if current_user != post.author :
        return render_template('info.html',info = 'only author can edit it!!')
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.last_change_time = datetime.now()
        db.session.add( post )
        db.session.commit()
        return redirect( url_for(".get_post",id=id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('edit_post.html',form=form)

@main.route("/follow_<username>.html")
@login_required
def follow(username):
    target_user = User.query.filter_by( username=username).first()
    if target_user is not None and current_user.is_following( target_user) is False:
        current_user.follow( target_user )
    return redirect( url_for('.user',name=username))
    #return render_template('info.html',info = '关注'+username+'? 待完善')

@main.route("/unfollow_<username>.html")
@login_required
def unfollow(username):
    target_user = User.query.filter_by( username=username).first()
    if target_user is not None and current_user.is_following( target_user) is True:
        current_user.unfollow( target_user )
    return redirect( url_for('.user',name=username))
    #return render_template('info.html',info = '取消关注'+username+'? 待完善')

@main.route("/followers_<username>.html")
@login_required
def followers(username):
    target_user = User.query.filter_by( username=username).first()
    all_followers =[ f.follower for f in target_user.followers.all() ]
    return render_template('user.html',user = target_user,followers = all_followers )
    #return render_template('info.html',info = '获得关注了'+username+'的? 待完善')

@main.route("/followed_by_<username>.html")
@login_required
def followed_by(username):
    target_user = User.query.filter_by( username=username).first()
    all_followed =[ f.followed for f in target_user.followed.all() ]
    return render_template('user.html',user = target_user,followed = all_followed )
    #return render_template('info.html',info = '获得被'+username+'关注的? 待完善')
