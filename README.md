# Project 1

Web Programming with Python and JavaScript

This a small web project for the CS50’s Web Programming with Python and JavaScript.

It's a small book database in which you can search using ISBN,
author name or book name. It shows up a list of results and after clicking on
any of them (if they're any results), it brings you to a more detailed book page
that shows additional details such as the amount of reviews, the average
rating from Goodreads(both using its API), along with other user reviews and
ratings. If your username hasn't uploaded a review, a text box will appear
allowing you to add it, along with a number rating.

What's contained in each file?

.env (not shown in github): automatically added environmental variables for the
virtual environment.

.gitignore: file that indicates files to be ignored while uploading to github.

README.md: this same file.

application.py: main flask file, contains all of the necessary background code.
(for more information, check the file itself, the code is well commented)

books.csv: file to import into the database with import.py

import.py: connects to the database and adds files from the books.csv file

requirements.txt: installed packages necessary for the project to run

images/wallpaper.jpg: background image

static/styles/layout.css: simple css file to slightly improve aesthetics.

templates/book.html: shows list of results from search.html in table form, if any

templates/book_details.html: after clicking on a result from book.html,
it shows you this page which shows additional book details, additional details
such as the amount of reviews, the average
rating from Goodreads(both using its API), along with other user reviews and
ratings. If your username hasn't uploaded a review, a text box will appear
allowing you to add it, along with a number rating.

templates/book_details.html/<isbn>: gives a json file of the book with basic
information, including data from goodreads.

templates/error.html: error page that shows a different message according to the
error, such as too short a password when registering or trying to login with a
username and password that is not in the database.

templates/layout.html: base html file that most of the other html files on the
same directory extend from and inherit, including bootstrap styles.
also, includes header, middle and footer cards. the middle one to be filled in
by whatever content other pages have.

templates/login.html: html page with forms that go into application.py,
the search section though. you can login here by using your username and password.
it'll compare your password with the user's hashed password in the database.

templates/logout.html: logs you out. to continue using the webpage you'd need
to log back in

templates/register.html: you can register here, it'll hash the password.
both the password and password confirmation need to be the same and 8+
characters long.

templates/review_post.html: page confirming that your review has been added to the database.

templates/search.html: page where you can search through the book database
by ISBN, author name or book title.


