#!/bin/env python2.7
#! -*- coding: UTF-8 -*-
from flask import abort
from functools import wraps
from flask.ext.login import current_user
from .models import Permission

def permission_required( permission ):
    def _in_decorator(func):
        @wraps(func)
        #用wraps修改被封装函数的__name__、__module__、__doc__和 __dict__
        def decorator_func(*args,**kwargs):
            if not current_user.check_permission( permission ):
                abort( 403)
            return func( *args, **kwargs)
        return decorator_func
    return  _in_decorator


def admin_required(func):
    return permission_required( Permission.ADMINISTER )( func )
