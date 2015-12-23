#!/bin/env python2.7
#! -*- coding: UTF-8 -*-
from . import api
from flask import g,jsonify,request,url_for
from ..models import Post,Comment,Permission
from decorators import permission_required
from .. import db

'''
api.get_user
api.get_post_comments
api.get_user
api.get_user_posts
api.get_user_followed_posts
'''
@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404( id )
    return jsonify( post.to_json())

@api.route('/posts/<int:id>/comments')
def get_post_comments(id):
    post = Post.query.get_or_404( id )
    page = request.args.get('page',1,type=int)
    pagination = post.comments.order_by( Comment.create_time.desc()).paginate(
            page,per_page=5,error_out=False )
    comments = pagination.items
    prev_page,next_page = None,None
    if pagination.has_prev:
        prev_page = url_for('api.get_post_comments',id=id,page=page-1,_external=True)
    if pagination.has_next:
        next_page = url_for('api.get_post_comments',id=id,page=page+1,_external=True)
    return jsonify( {'comments' : [ comment.to_json() for comment in comments ],
        'next' : next_page,
        'prev' : prev_page,
        'total': pagination.total,
        })

@api.route('/posts/',methods=['POST'])
@permission_required( Permission.ADMINISTER )
def new_post():
    post = Post.from_json( request.json )
    post.author = g.current_user
    db.session.add( post )
    db.session.commit()
    #返回(json数据，状态码，额外的Header信息)
    return jsonify(post.to_json()),201,{'location':url_for('api.get_post',id=post.id,_external=True)}
