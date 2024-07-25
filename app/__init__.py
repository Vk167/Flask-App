import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_session import Session
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__, instance_relative_config=False)
app.config.from_object("config.config")

def init_app():
    global app

    with app.app_context():
        from . import routes
        from Dash.app import init_dashboard
        app = init_dashboard(app)
        return app

app.secret_key = 'sessionkey@123456'

jwt = JWTManager(app)

app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize the Flask-Session
Session(app)

# Set up logging
if not os.path.exists("logs"):
    os.mkdir("logs")

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler('logs/app.log', maxBytes=10 * 1024 * 1024, backupCount=5)
log_handler.setFormatter(log_formatter)
app.logger.addHandler(log_handler)


# from . import routes