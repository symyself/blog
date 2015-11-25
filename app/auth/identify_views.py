# coding: utf-8
from flask import session,request
from identify_code import identify as image

from . import auth

@auth.route('/identify')
def identify():
    '''
    验证码图片
    '''
    #ca = identify.verify_img(request, 300, 60)
    #if session['answer'] != None:
    if 'answer' in session:
        print 'old answer:%s' %session['answer']
        session.pop('answer',None)
    ca = image.verify_img(request, 150, 34)
    print 'set verify code answer:%s' %session['answer']
    return ca.display()
