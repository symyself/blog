#!/bin/env python2.7
#! -*- coding: UTF-8 -*-
import unittest
from flask import current_app
from app.models import User,Role,Post,Permission,AnonymousUser
from app import create_app,db

class UserModelTestCase(unittest.TestCase):
    def setUp( self ):
        self.app    =   create_app('test')
        self.app_context    =   self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        User.generate_fake(count=5)
        Post.generate_fake( count=5)

    def tearDown( self ):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u =  User(username='songy',password='songy',email='mymellls@fffmmm.com')
        self.assertTrue( u.password_hash is not None )

    def test_no_password_getter(self):
        u =  User(username='songy',password='songy',email='mymellls@fffmmm.com')
        #with self.assertLessEqual(AttributeError):
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u =  User(username='songy',password='songy',email='mymellls@fffmmm.com')
        self.assertTrue( u.verify_password( 'songy' ) )
        self.assertFalse( u.verify_password( '123321' ) )

    def test_same_password_has_different_hash(self):
        u =  User(username='songy',password='songy',email='mymellls@fffmmm.com')
        u2 =  User(username='songyang',password='songy',email='songyang@fffmmm.com')
        self.assertTrue( u.password_hash != u2.password_hash )

    def test_generate_confirm_token(self):
        u =  User(username='songy',password='songy',email='mymellls@fffmmm.com')
        db.session.add(u)
        db.session.commit()
        token=u.generate_confirmation_token()
        self.assertTrue( u.confirm(token) )

    def test_chenge_email(self):
        u =  User(username='songy',password='songy',email='mymellls@fffmmm.com')
        db.session.add(u)
        db.session.commit()
        token = u.generage_change_email_token( new_email='46922184@qq.com')
        self.assertTrue( u.change_email(token) )

    def test_chenge_password(self):
        u =  User(username='songy',password='songy',email='mymellls@fffmmm.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_password_token()
        self.assertTrue( u.reset_password( new_password = '9999999991sdljflj' ))

    #测试权限
    def test_role_and_permission(self):
        Role.insert_roles()
        u =  User(username='songy',password='songy',email='mymellls@fffmmm.com')
        self.assertTrue( u.check_permission( Permission.WRITE_ARTICLES ))
        self.assertFalse( u.check_permission( Permission.ADMINISTER ))

    def test_anonymous_user( self):
        u = AnonymousUser()
        self.assertFalse( u.check_permission( Permission.FOLLOW ))
