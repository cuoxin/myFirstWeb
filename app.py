from flask import Flask, render_template, url_for, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import click


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db') ## 注意linux 为 sqlite:////
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev' ## 相当于 app.secret_key = 'dev'  建议为随机值


db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60)) # 电影标题
    year = db.Column(db.String(4)) # 电影年份


@app.cli.command() # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')
# 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop: # 判断是否输入了选项
        db.drop_all()
        db.create_all()
        click.echo('Initialized database.') 


@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.') ## 第一个参数会大写
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.') ## 3 密码隐藏 4 重复输入
def admin(username, password):
    ''' Creat User '''
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo("Updating ...")
        user.username = username
        user.set_password(password)
    else:
        click.echo("Creat ...")
        user = User(username=username, name="Admin")
        user.set_password(password=password)
        db.session.add(user)
    
    db.session.commit()
    click.echo("Done")


login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password') ## 原代码 .. = request.form['password'] 报错
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n", request.form)

        if not username or not password:
            flash("Invalid input")
            return redirect(url_for("login"))

        user = User.query.first()
        # print(">>>>>>>>>>>>>>>>\n", user)
        if user.username == username and user.validate_password(password):
            login_user(user)
            flash("Login Sucess")
            return redirect(url_for("index"))

        flash("Invalid username or password")
        return redirect(url_for("login"))
    return render_template("login.html")


login_manager.login_view = 'login'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('GoodBye')
    return redirect(url_for("index"))


@app.route('/settings', methods=["GET", "POST"])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input')
            return redirect(url_for("settings"))
        
        current_user.name = name
        db.session.commit()
        flash("Setting updated")
        return redirect(url_for("index"))
    
    return render_template("settings.html")
    


@app.context_processor
def inject_user():
    ''' 上下文统一注入变量 '''
    user = User.query.first()
    return dict(user=user)


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST': ## 判断是否为 POST 请求
        if not current_user.is_authenticated:
            return redirect(url_for("index"))
        ## 获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash("Invalid input") ## 提示信息
            return redirect(url_for('index')) ## 重定向
        else:
            movie = Movie(title=title, year=year)
            db.session.add(movie)
            db.session.commit()
            flash("Item created")
            return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template('index.html', movies = movies)

@app.route('/movie/edit/<int:movie_id>', methods=["GET", "POST"])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    # print(">>>>>>>>>>>>>\n", movie)

    if request.method == "POST":
        title = request.form["title"]
        year = request.form["year"]
        # print(">>>>>>>>>>>>>>>\n", request.form)
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash("Invalid input") ## 提示信息
            return redirect(url_for("edit", movie_id=movie_id))
        else:
            movie.title = title
            movie.year = year
            db.session.commit()
            flash("Item updated")
            return redirect(url_for("index"))
    return render_template('edit.html', movie=movie)
        

@app.errorhandler(404)
def pag_not_found(e):
    return render_template('404.html'), 404