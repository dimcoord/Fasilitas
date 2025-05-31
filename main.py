from flask import Flask

app = Flask(__name__)

@app.route("/")
def homepage():
    return "<p>Selamat datang di aplikasi web Fasilitas</p>"

@app.route("/login")
def login():
    return "<p>Tempat login</p>"

@app.route("/register")
def register():
    return "<p>Register</p>"

@app.route("/list")
def list():
    return "<p>List fasilitas yang dapat dipinjam</p>"

@app.route("/pinjam")
def pinjam():
    return "<p>Page untuk peminjaman</p>"