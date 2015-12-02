#!/bin/env python2.7
#! -*- coding: UTF-8 -*-
import unittest
from flask import current_app
from app.models import User,Role,Permission,AnonymousUser
from app import create_app,db

class UserModelTestCase(unittest.TestCase):
    def setUp( self ):
        self.app    =   create_app('test')
        self.app_context    =   self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown( self ):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u =  User(username='songy',password='songy',email='symyself@foxmail.com')
        self.assertTrue( u.password_hash is not None )

    def test_no_password_getter(self):
        u =  User(username='songy',password='songy',email='symyself@foxmail.com')
        #with self.assertLessEqual(AttributeError):
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u =  User(username='songy',password='songy',email='symyself@foxmail.com')
        self.assertTrue( u.verify_password( 'songy' ) )
        self.assertFalse( u.verify_password( '123321' ) )

    def test_same_password_has_different_hash(self):
        u =  User(username='songy',password='songy',email='symyself@foxmail.com')
        u2 =  User(username='songyang',password='songy',email='songyang@foxmail.com')
        self.assertTrue( u.password_hash != u2.password_hash )

    #测试权限
    def test_role_and_permission(self):
        Role.insert_roles()
        u =  User(username='songy',password='songy',email='symyself@foxmail.com')
        self.assertTrue( u.check_permission( Permission.WRITE_ARTICLES ))
        self.assertFalse( u.check_permission( Permission.ADMINISTER ))

    def test_anonymous_user( self):
        u = AnonymousUser()
        self.assertFalse( u.check_permission( Permission.FOLLOW ))
