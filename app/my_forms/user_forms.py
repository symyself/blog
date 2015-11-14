# encoding: utf-8
from flask.ext.wtf import Form
from wtforms import BooleanField, PasswordField, validators, StringField, SubmitField
'''
from wtforms import Form, BooleanField, TextField, PasswordField, validators, StringField, SubmitField

class register_form(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('email', [validators.Length(min=6, max=35)])
    password = PasswordField('password', [
        validators.Required(), validators.EqualTo('confirm', message='password must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.required()])
'''

class register_form(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('email', [validators.Length(min=6, max=35)])
    password = PasswordField('password', [
        validators.data_required('enter your password'), validators.EqualTo('confirm', message='password must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.required()])
    submit = SubmitField('Register')


class login_form(Form):
    username = StringField('Username', [validators.data_required('enter your name'), validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.data_required('enter your password')])
    verify_code = StringField('Verify Dode', [validators.data_required('enter verify code')])
    submit = SubmitField('Login')
