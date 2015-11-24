#!/usr/bin/env python
#! -*- coding: UTF-8 -*-
from app import create_app, db
from app.models import user,Role
from flask.ext.script import Manager,Shell
from flask.ext.migrate import Migrate,MigrateCommand

app = create_app ('default')
manager = Manager(app)
migrate = Migrate(app,db)


def make_shell_context():
    '''
    每次启动 shell 会话都要导入数据库实例和模型，这真是份枯燥的工作。为了避免一直重复
    导入，我们可以做些配置，让 Flask-Script 的 shell 命令自动导入特定的对象。
    若想把对象添加到导入列表中， 我们要为 shell 命令注册一个 make_context 回调函数，如
    示例 5-7 所示。
    '''
    return dict(app=app,db=db,user=user,Role=Role)
manager.add_command('shell',Shell(make_context=make_shell_context))

'''
为了导出数据库迁移命令， Flask-Migrate 提供了一个 MigrateCommand 类，可附加到 FlaskScript 的
manager 对象上。在这个例子中， MigrateCommand 类使用 db 命令附加。 在维护数据库迁移之前，要使用
init 子命令创建迁移仓库:
(venv) $ python hello.py db init
'''
manager.add_command('db',MigrateCommand)


@manager.command
def test():
    '''
    Run the unit test
    manager.command 修饰器让自定义命令变得简单。修饰函数名就是命令名，函数的文档字符
    串会显示在帮助消息中。 test() 函数的定义体中调用了 unittest 包提供的测试运行函数。
    单元测试可使用下面的命令运行：
    (venv) $ python manage.py test
    '''
    import unittest
    #tests   = unittest.TestLoader.discover( 'tests' )
    #unittest.TextTestRunner.run( tests )
    tests   = unittest.TestLoader().discover( 'tests' )
    unittest.TextTestRunner(verbosity=2).run( tests )


if __name__ == '__main__':
    manager.run()
    #manager.run(host='0.0.0.0',port=6666,debug=True)

###from first_flask import app
###app.debug = True
###if __name__ == '__main__':
###    app.run(host='0.0.0.0', port=1024, debug=True)
