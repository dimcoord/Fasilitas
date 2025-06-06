from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import InputRequired, Length, NumberRange, ValidationError
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
    reservasi = db.relationship('Reservasi', backref='user', lazy=True)
    
    def __repr__(self):
        return '<Task %r>' % self.id

class Fasilitas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    available_amount = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    is_deleted = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reservasi = db.relationship('Reservasi', backref='fasilitas', lazy=True)
    
    def __repr__(self):
        return '<Task %r>' % self.id
    
class Reservasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fasilitas_id = db.Column(db.Integer, db.ForeignKey('fasilitas.id'), nullable=False)
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
    password = PasswordField(validators=[InputRequired(), Length(
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
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={'placeholder': 'Password'})
    submit = SubmitField('Login')
    
class FacilityForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(
        min=4, max=50)], render_kw={'placeholder': 'Nama fasilitas'})
    total_amount = IntegerField(validators=[InputRequired(), NumberRange(
        min=1, max=100)], render_kw={'placeholder': 'Jumlah total'})
    available_amount = IntegerField(validators=[InputRequired(), NumberRange(
        min=1, max=100)], render_kw={'placeholder': 'Jumlah tersedia'})
    submit = SubmitField('Submit')
    
    def validate_available_amount(self, field):
        if self.total_amount.data is not None and field.data > self.total_amount.data:
            raise ValidationError('Fasilitas tersedia tidak boleh lebih dari total!')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and not user.is_deleted:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("list"))
            else:
                return '<p>Username/password salah!</p>'

    if not current_user:
        return render_template('login.html', form=form)
    else:
        return redirect(url_for('list'))

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
    
    if not current_user:
        return render_template('register.html', form=form)
    else:
        return redirect(url_for('list'))

@app.route("/list", methods=['POST', 'GET'])
@login_required
def list():
    username = current_user.username
    is_admin = current_user.is_admin
    fasilitas = Fasilitas.query.order_by(Fasilitas.id).all()
    return render_template('list.html', fasilitas=fasilitas, is_admin=is_admin, username=username)

@app.route("/list/<int:fasilitas_id>", methods=['POST', 'GET'])
@login_required
def list_detail(fasilitas_id):
    fasilitas = Fasilitas.query.get(fasilitas_id)
    if fasilitas:
        return render_template('pinjam.html', fasilitas=fasilitas)
    else:
        return render_template('404.html')

@app.route("/pinjam/<int:fasilitas_id>", methods=['POST', 'GET'])
@login_required
def pinjam(fasilitas_id):
    fasilitas = Fasilitas.query.get(fasilitas_id)
    if fasilitas and fasilitas.available_amount > 0:
        updateAvail = update(Fasilitas).where(Fasilitas.id == fasilitas.id).values(available_amount=Fasilitas.available_amount-1)
        db.session.execute(updateAvail)
        db.session.add(Reservasi(fasilitas_id=fasilitas.id, user_id=current_user.id))
        db.session.commit()
        return redirect(url_for('list'))
    else:
        return render_template('404.html')

@app.route("/reservasi", methods=['POST', 'GET'])
@login_required
def reservasi():
    username = current_user.username
    if current_user.is_admin:
        reservasi = Reservasi.query.order_by(Reservasi.id).all()
        return render_template('reservasi.html', reservasi=reservasi, username=username)
    else:
        return redirect(url_for('list'))

@app.route("/pengembalian/<int:reservasi_id>", methods=['POST', 'GET'])
@login_required
def reservasi_delete(reservasi_id):
    reservasi = Reservasi.query.get(reservasi_id)
    if reservasi:
        db.session.delete(reservasi)
        db.session.commit()
        return redirect(url_for('list'))
    else:
        return render_template('404.html')

# CRUD
# CRUD  
# CRUD
@app.route("/tambah", methods=['POST', 'GET'])
@login_required
def tambah():
    form = FacilityForm()
    
    if form.validate_on_submit():
        new_facility = Fasilitas(name=form.name.data, available_amount=form.available_amount.data, total_amount=form.total_amount.data)
        db.session.add(new_facility)
        db.session.commit()
        return redirect(url_for('list'))
    
    if current_user.is_admin:
        return render_template('tambah.html', form=form)
    else:
        return redirect(url_for('list'))
    
@app.route("/edit/<int:fasilitas_id>", methods=['POST', 'GET'])
@login_required
def edit(fasilitas_id):
    form = FacilityForm()
    fasilitas = Fasilitas.query.get(fasilitas_id)
    if fasilitas:
        # updateAvail = update(Fasilitas).where(Fasilitas.id == fasilitas.id).values(available_amount=Fasilitas.available_amount-1)
        # db.session.execute(updateAvail)
        # db.session.commit()
        return render_template('edit.html', form=form)
    else:
        return render_template('404.html')
    
@app.route("/delete/<int:fasilitas_id>", methods=['POST', 'GET'])
@login_required
def delete(fasilitas_id):
    fasilitas = Fasilitas.query.get(fasilitas_id)
    if fasilitas:
        db.session.delete(fasilitas)
        db.session.commit()
        return redirect(url_for('list'))
    else:
        return render_template('404.html')