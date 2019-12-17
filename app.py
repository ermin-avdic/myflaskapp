from flask import Flask, render_template, flash, redirect, request, url_for, session, logging
from flask_sqlalchemy import SQLAlchemy
from data import Articles
from datetime import datetime
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import psycopg2
import sys

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:toor@localhost/myflaskapp'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class UserInfo(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email= db.Column(db.String(200))
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    register_date = db.Column(db.DateTime, default='datetime.now')

    def __init__(self, name, email, username, password):
        self.name = name
        self.email = email
        self.username = username
        self.password = password

Articles = Articles()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles = Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match.')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():

        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        con = psycopg2.connect("dbname=myflaskapp user=postgres password=toor")
        cur = con.cursor()

        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        con.commit()

        cur.close()

        flash('You are now registerd and can log in', 'success')

        return redirect(url_for('index'))

    return render_template('register.html', form=form)

con = psycopg2.connect("dbname=myflaskapp user=postgres password=toor")
cur = con.cursor()

result = cur.execute("SELECT * FROM public.users")

print(result, flush=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password_candidate = request.form['password']

        con = psycopg2.connect("dbname=myflaskapp user=postgres password=toor")
        cur = con.cursor()

        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        print("test", flush=True)
        sys.stdout.flush()

        if result > 0:
            data = cur.fetchone()
            #for u in cur.fetchone():
            #    result_data = u.__dict__
            password = result_data['password']

            if sha256_crypt.verify(password_candidate, password):
                app.logger.info('PASSWORD MATCHED')

        else:
            app.logger.info('NO USER')

    return render_template('login.html')

if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run()