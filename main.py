
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '3pcknela94kep'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, name, password):
        self.name = name
        self.password = password

@app.route('/logout', methods=['GET'])
def logout():
    if 'name' in session:
        del session['name']
        flash("Successfully logged out")
        return redirect('/blog')
    else:
        flash("No users were currently logged in",'error')
        return redirect('/blog')
@app.before_request
def require_login():
    not_allowed_routes = ['newpost']
    if request.endpoint in not_allowed_routes and 'name' not in session:
        flash('Need to login in order to make a new post', 'error')
        return redirect('/login')

@app.route('/newpost', methods=['GET','POST'])
def newpost():
    if request.method=='GET':
        if 'name' in session:
            flash("Currently logged in as " + session['name'])
        return render_template('Add.html')
    else:
        title = request.form['title']
        body = request.form['body']
        titleerror = ""
        bodyerror = ""
        dbtitle = Blog.query.get('title')
        if((not title) or (title.strip() == "")):
            titleerror = "Not a valid blog title!"
        if((not body) or (body.strip() == "")):
            bodyerror = "Not a valid blog body!"
        
        if(titleerror + bodyerror != ""):
            return render_template('Add.html', title=title, body=body, bodyerror=bodyerror, titleerror=titleerror)

        owner = user.query.filter_by(name=session['name']).first()
        blog = Blog(title=title, body=body, owner=owner)
        db.session.add(blog)
        db.session.commit()
        
        return redirect("/blog?id=" + str(blog.id))

@app.route('/signup', methods=['GET','POST'])
def signup():
    if 'name' in session:
        flash("Please logout before creating a new account")
        return redirect('/')
    else:
        if request.method=="POST":
            username = request.form['username']
            password = request.form['password']
            verify = request.form['verify']
            validU = ""
            validP = ""
            validV = ""

            currentU = user.query.all()
            for i in currentU:
                if i.name == username:
                    validU = "Username is taken"
                    return render_template('signup.html', validU=validU)

            if ((not username) or (username.strip() == "") or (len(username) < 3)):
                validU = "Invalid Username (Must be at least 3 characters long)"
                
            if((not password) or (password.strip() == "") or (len(password) < 3)):
                validP = "Invalid Password (Must be at least    3 characters long)"

            if verify != password:
                validV = "Password and Verify are different"
                
            if validU + validP + validV != "":
                return render_template('signup.html', validU=validU, validP=validP, validV=validV)
                

            newUser = user(name=username, password=password)
            db.session.add(newUser)
            db.session.commit()

            session['name'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if 'name' in session:
        flash("Logout to login to another account.")
        return redirect('/')
    else:
        if 'name' in session:
            flash("Currently logged in as " + session['name'])
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            User = user.query.filter_by(name=username).first()
            if User and User.password == password:
                session['name'] = username
                return redirect('/')
            elif User and User.password != password:
                flash("Incorrect Password", 'error')
                return render_template('login.html', username=username)
            else:
                flash("No user was found under that username", 'error')
                return render_template('login.html')
        else:
            return render_template('login.html')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if 'name' in session:
        flash("Currently logged in as " + session['name'])
    if request.args:
        id = request.args.get('id')
        if id:
            blog = Blog.query.get(id)
            return render_template('blogpost.html', blog=blog)
        else:
            blogUser = request.args.get('user')
            blogger = user.query.filter_by(name=blogUser).first()
            bloggerblogs = Blog.query.filter_by(owner_id=blogger.id).all()
            return render_template("singleUser.html", blogs=bloggerblogs)
    else:
        blogs = Blog.query.all()
        return render_template('allUsers.html', blogs=blogs)

@app.route('/', methods=['GET'])
def index():
    if 'name' in session:
        flash("Currently logged in as " + session['name'])
    authors = user.query.all()
    no_Users = ""
    if not authors:
        no_Users = "No users yet. Signup up a the top!"
        return render_template('authors.html', no_Users=no_Users)
    return render_template('authors.html', authors=authors)

if __name__ == '__main__':
    app.run()
