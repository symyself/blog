#!/bin/env python2.7
#! -*- coding: UTF-8 -*-
from . import api
from flask import g,jsonify
from ..models import Comment

'''
api.get_user
api.get_post_comments
api.get_user
api.get_user_posts
api.get_user_followed_posts
'''
@api.route('/comments/<int:id>')
def get_comment(id):
    comment= Comment.query.get_or_404(id)
    return jsonify( comment.to_json() )


