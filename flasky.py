import os
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Role, Permission, InstrumentModel

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

#app_context_processor在flask中被称作上下文处理器，借助app_context_processor我们可以让所有自定义变量在模板中可见
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, InstrumentModel=InstrumentModel, Role=Role, Permission=Permission)


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
