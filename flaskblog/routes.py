import secrets , os
from PIL import Image
from flaskblog.models import User, Post
from flaskblog import app , db , bcrypt
from flask import render_template , url_for , flash , redirect , request , abort
from flaskblog.forms import RegistrationForm , LoginForm , UpdateAccountForm , PostForm
from flask_login import login_user , logout_user , login_required , current_user
#we moved it down because it failed earlier beacuse it havent seen the db variable yet , not that it has seen it itll no longer fail


# posts = [
#     {
#         'author' : 'Anusha Nikam',
#         'title' : 'Blog post 1',
#         'content' : 'this is my blog post 1',
#         'date' : 'April 20 , 2025'
#     },
#     {
#         'author' : 'Sahil Ranjan',
#         'title' : 'Blog post 2',
#         'content' : 'this is my blog post 2',
#         'date' : 'April 21 , 2025'
#     }

# ]

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/About")
def about_page():
    return render_template('about.html' , title = "About")

@app.route("/Home")
def home_page():
    # a query parameter to get othe pages in the url
    page = request.args.get ('page' , 1 , type = int)
    # we will paginate this to get a certain number of posts per page 
    # to desc makes the latest post appear first
    posts =  Post.query.order_by(Post.date_posted.desc()).paginate(  page= page ,  per_page= 5)
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
            flash('login unsucicessful. please check username and password' , 'danger')
    return render_template('login.html' , title = 'login' , form = form)

@app.route("/Logout")
def logout_page():
    logout_user()
    return redirect(url_for('home_page'))


def save_picture(form_picture):
    # we are doing this to extract the filename and extention but the major importance is of extention
    random_hex = secrets.token_hex(8)
    _ , f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)

    # resize the image with pillow before we save it
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/Account" , methods = ['GET' , 'POST'])
@login_required
def account_page():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()  
        flash('Your account has been updated!' , 'success')
        return redirect(url_for('account_page'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static' , filename = 'profile_pics/' + current_user.image_file)
    return render_template('account.html' , title = 'Account' , image_file = image_file , form = form)

@app.route( "/Post/new" , methods = ['GET' , 'POST'])
@login_required
def new_post_page():
    form = PostForm()
    if form.validate_on_submit():
        post = Post( title = form.title.data , content = form.content.data , author = current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been created!" , 'success')
        return redirect(url_for('home_page'))
    return render_template('create_post.html' , title = 'New Post' , form = form)

@app.route( "/Post/<int:post_id>")
def post_page(post_id):
    # this template tell us that give me the post with the given id or else give me 404 error 
    post = Post.query.get_or_404(post_id)
    return render_template('post.html' , title = post.title , post = post)

@app.route( "/Post/<int:post_id>/update" , methods = ['GET' , 'POST'])
@login_required
def update_post_page(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        # we dont need to add it to the session because its already in the session
        db.session.commit()
        flash( 'Your post has been updated!' , 'success')
        return redirect( url_for( 'post_page' , post_id = post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html' , title = 'Update Post' , form = form)


@app.route( "/Post/<int:post_id>/delete" , methods = ['POST'])
@login_required
def delete_post_page(post_id):
    # this template tell us that give me the post with the given id or else give me 404 error 
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash( 'Your post has been deleted!' , 'success')
    return redirect(url_for('home_page'))

@app.route("/User/<string:username>")
def user_posts_page(username):
    # a query parameter to get othe pages in the url
    page = request.args.get ('page' , 1 , type = int)
    # we will paginate this to get a certain number of posts per page 
    # to desc makes the latest post appear first
    user = User.query.filter_by(username = username).first_or_404()
    posts =  Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(  page= page ,  per_page= 5)
    return render_template('user_posts.html' , posts = posts , user=user)