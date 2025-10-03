from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from flask_login import LoginManager

app = Flask(__name__)
# special variable name of the module 

app.config['SECRET_KEY'] = '5e1d3ae6517c3ae6c96bc92dd0702b07'
basedir = os.path.abspath(os.path.dirname(__file__))
#local path of the database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
Login_manager = LoginManager(app)
Login_manager.login_view = 'login_page'
Login_manager.login_message_category = 'info'

from flaskblog import routes
