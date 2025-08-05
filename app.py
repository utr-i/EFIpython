from flask import Flask, flash, render_template, request, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user,login_required,logout_user,current_user
)

app=Flask(__name__)

app.secret_key="cualquiercosa"
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://root:@localhost/miniblog"
)

db = SQLAlchemy(app)
migrate = Migrate(app,db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template(
        'index.html'
    )

@app.route('/login')
def login():
    
    return render_template('login.html')

@app.route('/register')
def register():
    
    return render_template('register.html')