import os

from flask import Flask # type: ignore

def create_app(test_config=None):
    # creates and configures the app
    # the secret key should be changed in prod
    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        #loads the instance config (default one) when not testing
        app.config.from_pyfile('config.py', silent = True)
    else:
        #loads the test configuration
        app.config.from_mapping(test_config)

    #ensure the instance folder (root, here it's flask-tutorial) exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import library
    app.register_blueprint(library.bp)
    app.add_url_rule('/', endpoint='index')

    return app
