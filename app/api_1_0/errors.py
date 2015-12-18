#!/bin/env python2.7
#! -*- coding: UTF-8 -*-
from flask import jsonify

def forbidden( message ):
    response = jsonify({'error':'forbidden','message':message})
    response.status_code = 403
    return response

def unauthorized( message ):
    response = jsonify({'error':'unauthorized','message':message})
    response.status_code = 401
    return response
