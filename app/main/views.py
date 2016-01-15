# coding: utf-8
from flask import render_template,flash,abort,redirect,url_for,request,abort
from flask.ext.login import current_user,login_required
from . import main
from ..models import Permission,User,Post,Comment
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

@main.route('/new_article',methods=['GET','POST'])
@login_required
@permission_required( Permission.WRITE_ARTICLES )
def new_article():
    form = user_forms.new_article_form()
    if form.validate_on_submit():
        title = form.title.data
        content =  form.content.data
        return render_template('new_article.html',form=form,title=title,content=content)
    else:
        return render_template('new_article.html',form=form)

@main.route('/moderate_comment.html')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_comment():
    page = request.args.get( 'page',1,type=int)
    pagination = Comment.query.order_by( Comment.create_time.desc()).paginate(
            page,per_page=5,error_out=False)
    comments=pagination.items
    return render_template( 'moderate_comment.html' ,
            comments=comments,pagination=pagination,page=page)

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



'''
在模板中可能也需要检查权限，所以 Permission 类为所有位定义了常量以便于获取。为了
避免每次调用 render_template() 时都多添加一个模板参数，可以使用上下文处理器。上
下文处理器能让变量在所有模板中全局可访问。
'''
@main.app_context_processor
def inject_permissions():
     return dict(Permission=Permission)

@main.route('/get_post_<id>.html',methods=['GET','POST'])
def get_post(id):
    post = Post.query.get_or_404(id)
    form = user_forms.comment_form()
    if form.validate_on_submit():
        comment = Comment( body=form.body.data,
                post=post,
                author=current_user._get_current_object())
        db.session.add( comment )
        db.session.commit()
        flash("your comment committed!!")
        return redirect(url_for(".get_post",id=id))
    page = request.args.get( 'page',1,type=int)
    if page == -1:
        #最后一页
        page = (post.comments.count() -1)/5 + 1
    pagination = post.comments.order_by( Comment.create_time.desc()).paginate(
            page,per_page=5,error_out=False)
    comments = pagination.items
    return render_template( 'post.html',form=form,posts=[post],
            comments=comments,pagination=pagination)


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
    all_followers =[ f.follower for f in target_user.followers.all() if f.follower != target_user ]
    return render_template('user.html',user = target_user,followers = all_followers )
    #return render_template('info.html',info = '获得关注了'+username+'的? 待完善')

@main.route("/followed_by_<username>.html")
@login_required
def followed_by(username):
    target_user = User.query.filter_by( username=username).first()
    all_followed =[ f.followed for f in target_user.followed.all() if f.followed != target_user ]
    return render_template('user.html',user = target_user,followed = all_followed )
    #return render_template('info.html',info = '获得被'+username+'关注的? 待完善')

@main.route('/get_followed_posts.html')
@login_required
def get_followed_posts():
    page = request.args.get( 'page',1,type=int)
    pagination = current_user.followed_posts.paginate(
            page,per_page=10,error_out=False)
    posts=pagination.items
    return render_template( 'followed_posts.html' ,posts=posts,pagination=pagination)

@main.route('/change_head_img.html')
@login_required
def change_head_img():
    current_user.head_img = current_user.get_random_head_img()
    db.session.add( current_user )
    return redirect( current_user.image_url() )

@main.route('/enable_comment_<int:id>.html')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def enable_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add( comment )
    db.session.commit()
    page = request.args.get( 'page',1,type=int)
    return redirect( url_for(".moderate_comment",page=page))

@main.route('/disable_comment_<int:id>.html')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def disable_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add( comment)
    db.session.commit()
    page = request.args.get( 'page',1,type=int)
    return redirect( url_for(".moderate_comment",page=page))

@main.route('/delete_comment_<int:id>.html')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete( comment )
    db.session.commit()
    page = request.args.get( 'page',1,type=int)
    return redirect( url_for(".moderate_comment",page=page))
