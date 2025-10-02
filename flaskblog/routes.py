from flaskblog.models import User, Post
from flaskblog import app , db , bcrypt
from flask import render_template , url_for , flash , redirect , request
from flaskblog.forms import RegistrationForm , LoginForm
from flask_login import login_user , logout_user , login_required , current_user
#we moved it down because it failed earlier beacuse it havent seen the db variable yet , not that it has seen it itll no longer fail


posts = [
    {
        'author' : 'Anusha Nikam',
        'title' : 'Blog post 1',
        'content' : 'this is my blog post 1',
        'date' : 'April 20 , 2025'
    },
    {
        'author' : 'Sahil Ranjan',
        'title' : 'Blog post 2',
        'content' : 'this is my blog post 2',
        'date' : 'April 21 , 2025'
    }

]

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/About")
def about_page():
    return render_template('about.html' , title = "About")

@app.route("/Home")
def home_page():
    return render_template('home.html' , posts = posts)

@app.route("/Register" , methods = ['GET' , 'POST'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #creating new instance of the user with new hashed password
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        # help us to redirect trying to go to home page after registering
        flash(f'Your account has been created! you are now able to login' , 'success')
        return redirect(url_for('home_page'))
    return render_template('register.html' , title = 'register' , form = form)

@app.route("/Login" ,  methods = ['GET' , 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            return redirect(url_for('home_page'))
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password , form.password.data):
             login_user( user , remember= form.remember.data)
             next_page = request.args.get('next')
             return  redirect(next_page) if next_page else redirect(url_for('home_page'))
        else:
            flash('login unsucicessful. please check username and passw ord' , 'danger')
    return render_template('login.html' , title = 'login' , form = form)

@app.route("/Logout")
def logout_page():
    logout_user()
    return redirect(url_for('home_page'))

@app.route("/Account")
@login_required
def account_page():
    return render_template('account.html' , title = 'Account')

