from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:somerandompassword@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'somerandompassword'

# Class for Blog db

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime)

    def __init_(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

# Class for User db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship('Blog', backref='owner')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


# Routing for app

@app.before_request
def require_login():
    allowed_routes = ['blog', 'login', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else: 
            flash("User does not exist or password is incorrect", "error")
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, email, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username
            return redirect('/newpost')
        else: 
            flash("Users must register before blogging", "error")
            #return redirect('/signup')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    flash('You are now logged out')
    return redirect('/')

@app.route('/blog')
def blog():
    if not request.args:
        posts = Blog.query.order_by(Blog.timestamp.desc()).all()   
        return render_template('blog.html', posts=posts)
    elif request.args.get('id'):
        user_id = request.args.get('id')
        post = Blog.query.filter_by(id=user_id).first()
        return render_template('blogpost.html', post=post)
    elif request.args.get('user'):
        user_id = request.args.get('user')
        user = User.query.filter_by(id=user_id).first()
        posts = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('user.html', posts=posts, user=user)

    
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        error = ""

        if not title or not body:
            error = "Please enter both a title and blog content"
            return render_template('newpost.html', error=error)
        else:
            post = Blog(title=title, body=body, owner=owner, timestamp=datetime.now())
            db.session.add(post)
            db.session.commit()
            return redirect('/blog') 
    
    if request.method == 'GET':
        return render_template('newpost.html')
    

@app.route("/")
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()