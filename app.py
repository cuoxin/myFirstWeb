from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db') ## 注意linux 为 sqlite:////
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60)) # 电影标题
    year = db.Column(db.String(4)) # 电影年份


@app.context_processor
def inject_user():
    ''' 上下文统一注入变量 '''
    user = User.query.first()
    return dict(user=user)


@app.route('/')
def index():
    movies = Movie.query.all()
    return render_template('index.html', movies = movies)


@app.errorhandler(404)
def pag_not_found(e):
    return render_template('404.html'), 404