import os

from flask import Flask
from flask_assets import Environment
from flask_compress import Compress
from flask_login import LoginManager
from flask_mail import Mail
from flask_rq import RQ
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
# from flask_admin import Admin
# from flask_admin.contrib.sqla import ModelView

from app.assets import app_css, app_js, vendor_css, vendor_js
from config import config

basedir = os.path.abspath(os.path.dirname(__file__))

mail = Mail()
db = SQLAlchemy()
csrf = CSRFProtect()
compress = Compress()
# admin = Admin()

# Set up Flask-Login
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'account.login'

# from app.models import User, OralHistory

from app.hypothesis import HypothesisClient

def create_app(config_name, url_prefix=""):
    app = Flask(__name__, static_url_path=url_prefix+"/static")
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # not using sqlalchemy event system, hence disabling it

    config[config_name].init_app(app)

    # Set up extensions
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    compress.init_app(app)
    RQ(app)
    # admin.init_app(app)
    # admin.add_view(ModelView(User, db.session))
    # admin.add_view(ModelView(OralHistory, db.session))

    # Register Jinja template functions
    from .utils import register_template_utils
    register_template_utils(app)

    # Set up asset pipeline
    assets_env = Environment(app)
    dirs = ['assets/styles', 'assets/scripts']
    for path in dirs:
        assets_env.append_path(os.path.join(basedir, path))
    assets_env.url_expire = True

    assets_env.register('app_css', app_css)
    assets_env.register('app_js', app_js)
    assets_env.register('vendor_css', vendor_css)
    assets_env.register('vendor_js', vendor_js)

    # Configure SSL if platform supports it
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask.ext.sslify import SSLify
        SSLify(app)

    hypothesis_service = os.environ.get('HYPOTHESIS_SERVICE', 'http://localhost:5000')
    hyp_client = HypothesisClient(authority=os.environ['HYPOTHESIS_AUTHORITY'],
                                  client_id=os.environ['HYPOTHESIS_CLIENT_ID'],
                                  client_secret=os.environ['HYPOTHESIS_CLIENT_SECRET'],
                                  jwt_client_id=os.environ['HYPOTHESIS_JWT_CLIENT_ID'],
                                  jwt_client_secret=os.environ['HYPOTHESIS_JWT_CLIENT_SECRET'],
                                  service=hypothesis_service)
    app.hypothesis_client = hyp_client

    # Create app blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix=url_prefix)

    from .account import account as account_blueprint
    app.register_blueprint(account_blueprint, url_prefix=url_prefix+'/account')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix=url_prefix+'/admin')

    from .experimental import experimental as experimental_blueprint
    app.register_blueprint(experimental_blueprint, url_prefix=url_prefix+'/experimental')

    return app
