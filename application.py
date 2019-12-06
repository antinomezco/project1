import os

from flask import Flask, session, render_template, request, jsonify, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
#from flask_wtf import FlaskForm # apparently necessary for CSRFProtect to work
from flask_wtf.csrf import CSRFProtect
#from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"): # gets the database URL as to connect to it
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False # manages the session for each user, as to make them separate from each other (not have user A see user B's data)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Set up Goodreads API key:
grkey = os.getenv("GOODREADS_API_KEY") #connects to the Goodreads API with a particular key that I got from them by signing up

#secret key for use with csrf
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Enabling jsonify pretty printing
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True #not sure if this works, but it's supposed to make such a page (ex. https://antinomy.pythonanywhere.com/book/0375913750) look prettier

# Setting up CSRF security
csrf = CSRFProtect(app)

@app.route("/")
@app.route("/login", methods=["GET","POST"])
def login_page():
    rmessage = None #this is none because it only gets data if you're coming from the register webpage
    if request.method == 'POST': #post means that another webpage posted data that goes to this page. this would be coming from the register page
        url = request.headers.get("Referer") #Gets the page where you're coming from, in this case, if you're coming from the register page
        if url == "https://antinomy.pythonanywhere.com/register":
            rmessage = "Thanks for registering, please log in" #the prev line checks whether you come from the register page. if so, then it puts the string phrase into the variable
        username = request.form.get("username") #gets the name from the form from the register page
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
        username = request.form.get("username") #get the data from the form coming from login
        password = request.form.get("password")
        user_match = db.execute("SELECT username, password, user_id FROM username_table WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone() #tries to find if the inputted username and password from the login page do actually exist in the database
        session['username']=username #puts the collected username in the session global variable which will keep track of the logged in user (just whether they're logged in or not)
        session['user_id']=user_match.user_id
        if user_match is None: #if there's no username and password match in the db, then it goes to the page below
            return render_template("error.html", message="Incorrect username and/or password.")
    if 'username' in session: #the previously mentioned session global variable is checked to verify that the user is logged on, if so then if loads the search.html page as shown below
        s = session['username'];
        return render_template('search.html', s = s, title=title)
    return render_template("error.html", message="Please log in.")

@app.route("/book", methods=["GET","POST"])
def book_page():
    title = "Search results page"
    search_box = "%" + str(request.form.get("search_term")) + "%" #request.form.get("search_term") gets whatever string you put in the previous search page and then adds a parentheses to both sides of the string to allow for partial searches
    select = ''.join(request.form.getlist('search_type')) #gets the tabbed information from the search page
    #try to make the following work to not use an if results = db.execute("SELECT title, author, isbn, year FROM books_table WHERE :select = :search_box", {"select": select, "search_box": search_box}).fetchall()
    if select == "isbn": #searches by isbn, if you chose so in the search page
        results = db.execute("SELECT title, author, isbn, year FROM books_table WHERE isbn ILIKE :search_box",
        {"select": select, "search_box": search_box}).fetchall()
    elif select == "author":
        results = db.execute("SELECT title, author, isbn, year FROM books_table WHERE author ILIKE :search_box",
        {"select": select, "search_box": search_box}).fetchall()
    elif select == "title":
        results = db.execute("SELECT title, author, isbn, year FROM books_table WHERE title ILIKE :search_box",
        {"select": select, "search_box": search_box}).fetchall()
    if 'username' in session: #keeps checking for the logged in user
        s = session['username'];
        return render_template('book.html', title=title, s = s, results=results,
        select=select, search_box=search_box) #defines the variables to be used inside the book.html jinja code
    return render_template("error.html", message="Please log in.")

@app.route("/book/<isbn_num>", methods=["GET","POST"])
def book_details(isbn_num):
    title = "Book details"
    if 'username' in session:
        s = session['username']
        goodreads_data = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": grkey, "isbns": isbn_num}).json()
        book_data = db.execute("SELECT books_table.isbn, books_table.title, books_table.author, books_table.year, review_table.review, review_table.rating, review_table.isbn FROM books_table LEFT JOIN review_table ON books_table.isbn = review_table.isbn WHERE books_table.isbn = :isbn AND review_table.user_id = :user_id", {"isbn": isbn_num, "user_id": session['user_id']}).fetchone()
        user_reviews = db.execute("SELECT review_table.review, review_table.rating, username_table.username FROM review_table, username_table WHERE review_table.user_id = username_table.user_id AND review_table.isbn=:isbn", {"isbn": isbn_num}).fetchall()
        if book_data is None:
            book_data = db.execute("SELECT books_table.isbn, books_table.title, books_table.author, books_table.year FROM books_table WHERE books_table.isbn = :isbn", {"isbn": isbn_num, "user_id": session['user_id']}).fetchone()
        if request.headers.get("Referer") == "https://antinomy.pythonanywhere.com/book":
            return render_template('book_details.html', title=title, s = s,
            book_data=book_data, goodreads_data=goodreads_data, isbn_num=isbn_num, user_reviews=user_reviews)
        if request.method == 'GET': #if you directly go to this webpage instead of following a link, this will appear
            try:
                return jsonify(
                    {"title":book_data.title,
                    "author":book_data.author,
                    "year":book_data.year, "isbn":book_data.isbn,
                    "review_count":goodreads_data["books"][0]["ratings_count"],
                    "average_rating":goodreads_data["books"][0]["average_rating"]
                    })
            except:
                abort(404)
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

