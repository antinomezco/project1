import os

from flask import Flask, session, render_template, request, jsonify
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

# Enabling jsonify pretty printing
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

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
        user_match = db.execute("SELECT username, password, user_id FROM username_table WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()
        session['username']=username
        session['user_id']=user_match.user_id
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
        results = db.execute("SELECT title, author, isbn, year FROM books_table WHERE isbn ILIKE :search_box",
        {"select": select, "search_box": search_box}).fetchall()
    elif select == "author":
        results = db.execute("SELECT title, author, isbn, year FROM books_table WHERE author ILIKE :search_box",
        {"select": select, "search_box": search_box}).fetchall()
    elif select == "title":
        results = db.execute("SELECT title, author, isbn, year FROM books_table WHERE title ILIKE :search_box",
        {"select": select, "search_box": search_box}).fetchall()
    if 'username' in session:
        s = session['username'];
        return render_template('book.html', title=title, s = s, results=results,
        select=select, search_box=search_box)
    return render_template("error.html", message="Please log in.")

@app.route("/book/<isbn_num>", methods=["GET","POST"])
def book_details(isbn_num):
    title = "Book details"
    if 'username' in session:
        s = session['username']
        #book_data = db.execute("SELECT books_table.isbn, books_table.title, books_table.author, books_table.year, review_table.review, review_table.rating FROM books_table, review_table WHERE books_table.isbn= review_table.isbn AND books_table.isbn = :isbn AND review_table.user_id = :user_id", {"isbn": isbn_num, "user_id": session['user_id']}).fetchone()
        book_data = db.execute("SELECT books_table.isbn, books_table.title, books_table.author, books_table.year, review_table.review, review_table.rating, review_table.isbn FROM books_table LEFT JOIN review_table ON books_table.isbn = review_table.isbn WHERE books_table.isbn = :isbn AND review_table.user_id = :user_id", {"isbn": isbn_num, "user_id": session['user_id']}).fetchone()
        if book_data is None:
            book_data = db.execute("SELECT books_table.isbn, books_table.title, books_table.author, books_table.year FROM books_table WHERE books_table.isbn = :isbn", {"isbn": isbn_num, "user_id": session['user_id']}).fetchone()
        goodreads_data = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": grkey, "isbns": isbn_num}).json()
        if request.headers.get("Referer") == "https://antinomy.pythonanywhere.com/book":
            return render_template('book_details.html', title=title, s = s,
            book_data=book_data, goodreads_data=goodreads_data, isbn_num=isbn_num)
        if request.method == 'GET':
            return jsonify(
                {"title":book_data.title,
                "author":book_data.author,
                "year":book_data.year, "isbn":book_data.isbn,
                "review_count":goodreads_data["books"][0]["ratings_count"],
                "average_rating":goodreads_data["books"][0]["average_rating"]})
    return render_template("error.html", message="Please log in.", title=title)

@app.route("/review_post", methods=["POST"])
def review_post_page():
    title = "Review post page"
    review = request.form.get("review")
    rating = request.form.get("rating")
    isbn = request.form.get("isbn")
    db.execute("INSERT INTO review_table (review, rating, isbn, user_id) VALUES (:review, :rating, :isbn, :user_id)", {"review": review, "rating": rating, "isbn": isbn, "user_id": session['user_id']})
    db.commit()
    if 'username' in session:
        s = session['username']
        return render_template("review_post.html", title=title, review=review, rating=rating, s=s)
    return render_template("error.html", message="Dunno wut happen, but something broke trying to post the review?", title=title)

@app.route("/register")
def register_page():
    title = "Register"
    return render_template("register.html", title=title)

@app.route("/logout")
def logout_page():
    if 'username' in session:
        session.pop('username',None)
        return render_template('logout.html')