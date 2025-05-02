#! C:\Users\Dima\Projects\ClassPlanner\venv\Scripts\python.exe
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__, template_folder= 'templates')

app.config['SECRET_KEY'] = 'randomkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///classplaner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'en'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
babel = Babel(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import routes, models