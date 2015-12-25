#!/bin/env python2.7
#! -*- coding: UTF-8 -*-
import unittest
import re
from flask import current_app,url_for
from app.models import User,Role,Permission,AnonymousUser
from app import create_app,db


class FlaskClientTestCase(unittest.TestCase):
    def setUp( self ):
        self.app    =   create_app('test')
        self.app_context    =   self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client( use_cookies=True)

    def tearDown( self ):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page( self ):
        print 'test_home_page'
        response = self.client.get(url_for('main.base'))
        self.assertTrue(b'Stranger' in response.data )

    def test_register_and_login( self ):
        '''测试一个完整的 注册-登录-退出 流程'''

        # register
        response = self.client.post(
                url_for('auth.register'),
                data={'username':'newusername',
                    'email':'songyang@vxinyou.com',
                    'password':'newpassword1234',
                    'confirm':'newpassword1234'}
                )
        #检查响应的状态码是否为 302，这个代码表示重定向。
        self.assertTrue( response.status_code == 302 )

        #confirm new user
        new_user = User.query.filter_by( username = 'newusername' ).first()
        new_user.confirmed = True
        db.session.add( new_user )
        db.session.commit()


        #login
        with self.client.session_transaction() as sess:
            ''' 设置session，验证码答案'''
            sess['answer'] = '12345'
        response = self.client.post(
                url_for('auth.login'),
                data={'username':'newusername',
                    'password':'newpassword1234',
                    'verify_code':'12345',
                    'remember_me':False},
                follow_redirects=True)
        data = response.get_data(as_text =  True)
        self.assertTrue( 'followed Posts' in data )

        #get user info
        response = self.client.get(url_for('main.user',name=new_user.username ))
        self.assertTrue( u'注册时间' in response.get_data(as_text =True ) )

        #logout
        response = self.client.get(url_for('auth.logout'),follow_redirects=True)
        self.assertTrue( 'you have logged out' in response.get_data( as_text = True ) )
