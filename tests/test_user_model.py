#!/bin/env python
import unittest
from app.models import user

class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u =  user(password='123')
        self.assertTrue( u.password_hash is not None )

    def test_no_password_getter(self):
        u = user(password='123')
        with self.assertLessEqual(AttributeError):
            u.password

    def test_password_verification(self):
        u = user(password='123')
        self.assertTrue( u.verify_password( '123' ) )
        self.assertFalse( u.verify_password( '123321' ) )
