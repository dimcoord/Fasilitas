from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    is_admin = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Task %r>' % self.id

with app.app_context():
    db.create_all()
    print(">>>Database tables checked/created.<<<")

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={'placeholder': 'Username'})
    password = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={'placeholder': 'Password'})
    phone_number = StringField(validators=[InputRequired(), Length(
        min=10, max=15)], render_kw={'placeholder': 'No. WhatsApp Aktif'})
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        existing_username = User.query.filter_by(username=username.data).first()
        if existing_username:
            raise ValidationError('Username sudah terdaftar!')
        
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={'placeholder': 'Username'})
    password = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={'placeholder': 'Password'})
    submit = SubmitField('Login')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                redirect(url_for('list'))
            else:
                print('Try again')

    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/register", methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password, phone_number=form.phone_number.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route("/list", methods=['POST', 'GET'])
@login_required
def list():
    return render_template('list.html')

@app.route("/pinjam", methods=['POST', 'GET'])
@login_required
def pinjam():
    if request.method == 'POST':
        pass
    else:
        return render_template('pinjam.html')