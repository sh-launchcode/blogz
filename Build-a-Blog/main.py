#Contributors: Melinda Hunsaker

from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Build-a-Blog:buildablog@localhost:8889/Build-a-Blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    return render_template('Add.html')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method == 'POST':
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

        blog = Blog(title=title, body=body)
        db.session.add(blog)
        db.session.commit()
        
        return redirect("/blog?id=" + str(blog.id))

    else:
        if(request.args):
            id = request.args.get('id')
            blog = Blog.query.get(id)
            return render_template('blogpost.html', blog=blog)
            
        else:
            blogs = Blog.query.all()
            return render_template('index.html', blogs=blogs)

@app.route('/')
def index():
    return redirect("/blog")

if __name__ == '__main__':
    app.run()
