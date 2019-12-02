import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests, json
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

# Set up Goodreads API key:
grkey = os.getenv("GOODREADS_API_KEY")

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
        return render_template('search.html', s = s)
    return render_template("search.html", title=title, s=s)

@app.route("/book", methods=["GET","POST"])
def book_page():
    title = "Search results page"
    search_box = "%" + str(request.form.get("search_term")) + "%"
    select = ''.join(request.form.getlist('search_type'))
    #try to make the following work to not use an if results = db.execute("SELECT title, author, isbn, year FROM books_table WHERE :select = :search_box", {"select": select, "search_box": search_box}).fetchall()
    if select == "isbn":
        results = db.execute("SELECT title, author, isbn, year FROM books_table WHERE isbn ILIKE :search_box", {"select": select, "search_box": search_box}).fetchall()
    elif select == "author":
        results = db.execute("SELECT title, author, isbn, year FROM books_table WHERE author ILIKE :search_box", {"select": select, "search_box": search_box}).fetchall()
    elif select == "title":
        results = db.execute("SELECT title, author, isbn, year FROM books_table WHERE title ILIKE :search_box", {"select": select, "search_box": search_box}).fetchall()
    if 'username' in session:
        s = session['username'];
        return render_template('book.html', title=title, s = s, results=results, select=select, search_box=search_box)
    return render_template("error.html", message="Please log in.")

@app.route("/book/<isbn_num>")
def book_details(isbn_num):
    title = "Book details"
    data = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": grkey, "isbns": isbn_num}).json()
    book_data = db.execute("SELECT * FROM books_table WHERE isbn = :isbn", {"isbn": isbn_num}).fetchone()
    if 'username' in session:
        s = session['username'];
        return render_template('book_details.html', title=title, s = s, book_isbn=book_data, data=data)
    if book_data is None:
        return render_template("error.html", message="No book with that ISBN exists")
    return render_template("error.html", message="Please log in.", title=title, s=s)

@app.route("/register")
def register_page():
    title = "Register"
    return render_template("register.html", title=title)

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