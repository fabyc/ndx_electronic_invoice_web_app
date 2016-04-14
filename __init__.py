import psycopg2
import psycopg2.extras
import os
from flask import Flask, render_template, request, flash, redirect, session, url_for, request, g
from flask_sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, logout_user, current_user, \
    login_required
from flask.ext.openid import OpenID

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
CSRF_ENABLED = True
SECRET_KEY = 'secret_key'
DEBUG = True
app.config['SQLALCHEMY_DATABASE_URI'] = '/var/run/postgresql/.s.PGSQL.5432/usuarios'
app.config.from_object(__name__)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"
login_manager.setup_app(app)
db = SQLAlchemy(app)
 

