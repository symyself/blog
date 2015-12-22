#!/bin/env python2.7
#! -*- coding: UTF-8 -*-
from . import api
from flask import g,jsonify,url_for,request
from ..models import User,Post

@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404( id )
    return jsonify( user.to_json())

@api.route('/users/<int:id>/posts')
def get_user_posts(id):
    user = User.query.get_or_404( id )
    page = request.args.get('page',1,type=int)
    pagination = user.posts.order_by( Post.create_time.desc()).paginate(
            page,per_page=5,error_out=False )
    posts = pagination.items
    prev_page,next_page = None,None
    if pagination.has_prev:
        prev_page = url_for('api.get_user_posts',id=id,page=page-1,_external=True)
    if pagination.has_next:
        next_page = url_for('api.get_user_posts',id=id,page=page+1,_external=True)
    return jsonify( {'posts' : [ post.to_json() for post in posts ],
        'next' : next_page,
        'prev' : prev_page,
        'total': pagination.total,
        })

@api.route('/users/<int:id>/followed/posts')
def get_user_followed_posts(id):
    user = User.query.get_or_404( id )
    page = request.args.get('page',1,type=int)
    pagination = user.followed_posts.paginate(
            page,per_page=5,error_out=False )
    posts = pagination.items
    prev_page,next_page = None,None
    if pagination.has_prev:
        prev_page = url_for('api.get_user_posts',id=id,page=page-1,_external=True)
    if pagination.has_next:
        next_page = url_for('api.get_user_posts',id=id,page=page+1,_external=True)
    return jsonify( {'posts' : [ post.to_json() for post in posts ],
        'next' : next_page,
        'prev' : prev_page,
        'total': pagination.total,
        })
