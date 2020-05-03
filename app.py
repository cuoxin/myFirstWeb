from flask import Flask, url_for

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/user/<name>')
def user_page(name):
    return "User : {}".format(name)

@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page', name='Adrian'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for', num=2))
