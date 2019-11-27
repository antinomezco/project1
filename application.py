import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
#from werkzeug.security import generate_password_hash

app = Flask(__name__)

###app.secret_key = 'YouWillNeverGuessMySecretKey'

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

@app.route("/")
def index():
    title = "Home"
    return render_template("home.html", title=title)

@app.route("/login", methods=["GET","POST"])
def login_page():
    rmessage = None
    if request.method == 'POST':
        url = request.headers.get("Referer")
        if url == "https://antinomy.pythonanywhere.com/register":
            rmessage = "Thanks for registering, please log in"
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")
        if password != password_confirm:
            return render_template("error.html", message="Password mismatch.")
        db.execute("INSERT INTO username_table VALUES (:username, :password)", {"username": username, "password": password})
        db.commit()
    title = "Login"
    return render_template("login.html", title=title, rmessage=rmessage)

@app.route("/search", methods=["GET","POST"])
def search_page():
    title = "Search"
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user_match = db.execute("SELECT * FROM username_table WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()
        if user_match is None:
            return render_template("error.html", message="Incorrect username and/or password.")
    return render_template("search.html", title=title)

@app.route("/register")
def register_page():
    title = "Register"
    return render_template("register.html", title=title)

@app.route("/book")
def book_page():
    title = "Book"
    return render_template("book.html", title=title)

@app.route("/review")
def review_page():
    title = "Review"
    return render_template("review.html", title=title)

@app.route("/logout")
def logout_page():
    return render_template("logout.html")