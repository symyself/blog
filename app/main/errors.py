from flask import render_template,request,jsonify
from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    '''
    curl -H accept:application/json http://www.enjoy01.com/api/v1.0/posts/1030 
    http http://www.enjoy01.com/api/v1.0/posts/1030 Accept:application/json
    '''
    print 'accept_json',request.accept_mimetypes.accept_json
    print 'accept_html',request.accept_mimetypes.accept_html
    if request.accept_mimetypes.accept_json and \
        not request.accept_mimetypes.accept_html:
            response = jsonify({'error': 'not found'})
            response.status_code = 404
            return response
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    print 'accept_json',request.accept_mimetypes.accept_json
    print 'accept_html',request.accept_mimetypes.accept_html
    if request.accept_mimetypes.accept_json and \
        not request.accept_mimetypes.accept_html:
            response = jsonify({'error': 'internal_server_error'})
            response.status_code = 500
            return response
    return render_template('500.html'), 500

@main.app_errorhandler(403)
def permission_failed(e):
    return render_template('info.html',info = 'permission failed'),403
