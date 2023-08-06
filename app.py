from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy 
import json
from flask_mail import Mail, Message
import datetime 
 
 
 
app = Flask(__name__)
app.secret_key = "@sarman171"


global first_post

local_server = True
with open(".\static\config.json",mode="r") as con:
    file = json.load(con)
    parameter = file["params"]


if(local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = parameter["local_uri"]
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = parameter["production_uri"]
    
# initializing the app
db = SQLAlchemy(app)

# DB table for contacts
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String, unique=False, nullable=False)
    Email = db.Column(db.String(25), unique=False, nullable=False)
    Phno = db.Column(db.String(10), nullable=False)
    Msg = db.Column(db.String, nullable=False)
    
# DB table for posts
class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=False, nullable=False)
    slug = db.Column(db.String(30), unique=False, nullable=False)
    content = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=True)
    
class Login(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(15), unique=False, nullable=False)
    

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_username = request.form['username']
        login_password = request.form['password']
        
        if((login_username == parameter["login_user"] or login_username == parameter["gmail_id"]) and login_password == parameter["login_password"]):
            # Setting up the session
            session['username'] = login_username
            session['password'] = login_password
          
            # go to the index page
            return redirect(url_for("index"))
        else:
            return render_template('loginpage.html', parameter=parameter)
    else:
        if "username" and "password" in session:    # it means we r already logged in so it directly renders the logout page
              return redirect(url_for("index"))
        else:
            return render_template('loginpage.html', parameter=parameter)

@app.route('/index/', defaults={'page':1})
@app.route("/index/page/<int:page>")
def index(page):
    global first_post
    if "username" and "password" in session:
        first_post = Post.query.first_404()
        posts = Post.query.filter_by().all()
        
        page = request.args.get('page', 1, type=int)
        total_post = Post.query
        
        # slicing the posts into pages
        pages = total_post.paginate(page = page, per_page = parameter["no_of_posts"])
        
        
        return render_template('index.html', parameter=parameter, posts=posts, first_post = first_post, pages = pages)
    else:
        return render_template('loginpage.html', parameter = parameter)
    
    



@app.route("/about")
def about():
    if "username" and "password" in session:
        return render_template('about.html', parameter=parameter, first_post = first_post)
    else:
        return render_template('loginpage.html', parameter=parameter)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if "username" and "password" in session:
        if request.method == "POST":
            
            ''''Let's add some entries to the db'''
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            message = request.form.get('message')
            
            '''Saving the info in the database variables: sno, Name , Email , Phno , Msg'''
            entries = Contacts(Name = name, Email = email, Phno = phone, Msg = message)
            
            '''adding them in database'''
            db.session.add(entries)
            db.session.commit()
            
            
            # Setting up the mail system
            app.config['MAIL_SERVER']='smtp.gmail.com'
            app.config['MAIL_PORT'] = 465
            app.config['MAIL_USERNAME'] = parameter["gmail_id"]
            app.config['MAIL_PASSWORD'] = parameter["pswd"]
            app.config['MAIL_USE_SSL'] = True 
            app.config['MAIL_USE_TLS'] = False
            mail = Mail(app)

            # Sending the mail
            msg = Message('My post', sender = (name, email), recipients = [parameter["gmail_id"]])
            msg.body = message + "\n" + phone
            mail.send(msg)
            return redirect(url_for("post"))
        else:
            return render_template('contact.html', parameter=parameter, first_post = first_post)
    else:
        return render_template('loginpage.html', parameter = parameter)



@app.route("/sample_post/<string:p_slug>")
def post(p_slug):
    if "username" and "password" in session:
        post = Post.query.filter_by(slug = p_slug).first()
        return render_template('post.html', parameter=parameter, post=post, first_post = first_post)
    else:
        return render_template('loginpage.html', parameter=parameter, first_post = first_post)


@app.route("/edit/<int:sno>", methods=["POST", "GET"])
def edit(sno):
    if "username" and "password" in session:
        if request.method == "POST":
            title = request.form.get('title')
            slug = request.form.get('slug')
            content = request.form.get('content')
            date = datetime.datetime.now()
            
            
            if sno == 0:
                entries = Post(title = title, slug = slug, content = content, date = date)
            else:
                old_post = Post.query.get(sno)
                db.session.delete(old_post)
                db.session.commit()     
                entries = Post(sno = sno, title = title, slug = slug, content = content, date = date)
            db.session.add(entries)
            db.session.commit()

            return redirect(url_for("index"))
        else:
            return render_template("edit.html", parameter=parameter,  first_post = first_post)
            
    else:
        return render_template('loginpage.html', parameter = parameter)            

@app.route("/delete/<int:sno>")
def delete(sno):
    if "username" and "password" in session:
        old_post = Post.query.get(sno)
        db.session.delete(old_post)
        db.session.commit()     
        return redirect(url_for("index"))
    else:
        return render_template('loginpage.html', parameter = parameter)    
    

@app.route("/logout")
def logout():
    session.pop("username",None)
    session.pop("password",None)
    
    return redirect(url_for("login"))        

if __name__ == '__main__':
    app.run(debug=True)
    


