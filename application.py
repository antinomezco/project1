import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
#from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#def check_login():
#    if 'username' in session:
#        s = session['username'];
#        return render_template('search.html', title=title, s = s)

@app.route("/")
@app.route("/login", methods=["GET","POST"])
def login_page():
    rmessage = None
    if request.method == 'POST':
        url = request.headers.get("Referer") #Gets the page where you're coming from, in this case, if you're coming from the register page
        if url == "https://antinomy.pythonanywhere.com/register":
            rmessage = "Thanks for registering, please log in"
        username = request.form.get("username") #gets the name from the form
        password = request.form.get("password") #same, but for the password
        password_confirm = request.form.get("password_confirm") #confirms if the password is repeated correctly
        if password != password_confirm:
            return render_template("error.html", message="Password mismatch.")
        db.execute("INSERT INTO username_table VALUES (:username, :password)", {"username": username, "password": password}) #inserts the username and pass onto the db
        db.commit() #executes the prev INSERT command
    title = "Login"
    return render_template("login.html", title=title, rmessage=rmessage)

@app.route("/search", methods=["GET","POST"])
def search_page():
    title = "Search"
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user_match = db.execute("SELECT * FROM username_table WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()
        session['username']=username
        if user_match is None:
            return render_template("error.html", message="Incorrect username and/or password.")
    if 'username' in session:
        s = session['username'];
        return render_template('search.html',s = s)
    return render_template("search.html", title=title, s=s)

@app.route("/register")
def register_page():
    title = "Register"
    return render_template("register.html", title=title)

@app.route("/book")
def book_page():
    title = "Book"
    if 'username' in session:
        s = session['username'];
        return render_template('book.html', title=title, s = s)
    return render_template("error.html", message="Please log in.")

@app.route("/review")
def review_page():
    title = "Review"
    if 'username' in session:
        s = session['username'];
        return render_template('review.html', title=title, s = s)
    return render_template("error.html", message="Please log in.")

@app.route("/logout")
def logout_page():
    if 'username' in session:
        session.pop('username',None)
        return render_template('logout.html')