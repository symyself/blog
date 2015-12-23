#!/bin/env python2.7
#! -*- coding: UTF-8 -*-
from functools import wraps
from flask import g
from ..models import Permission
from .errors import forbidden

def permission_required( permission ):
    def _in_decorator(func):
        @wraps(func)
        #用wraps修改被封装函数的__name__、__module__、__doc__和 __dict__
        def decorator_func(*args,**kwargs):
            if not g.current_user.check_permission( permission ):
                return forbidden( 'permission_required ')
            return func( *args, **kwargs)
        return decorator_func
    return  _in_decorator


def admin_required(func):
    return permission_required( Permission.ADMINISTER )( func )
