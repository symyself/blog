#!/usr/bin/env python
from app import create_app, db
from app.models import user
from flask.ext.script import Manager,Shell

app = create_app ('default')
manager = Manager(app)


if __name__ == '__main__':
    manager.run()
    #manager.run(host='0.0.0.0',port=6666,debug=True)

###from first_flask import app
###app.debug = True
###if __name__ == '__main__':
###    app.run(host='0.0.0.0', port=1024, debug=True)
