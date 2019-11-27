import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

print("before main")

def main():
    print("start")
    f = open("books.csv")
    reader = csv.reader(f)
    #has_header = csv.Sniffer().has_header(f.read(1024))
    #if has_header:
    next(reader)  # Skip header row.
    for isbn, ttl, auth, yr in reader:
        db.execute("INSERT INTO books_table (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {"isbn": isbn, "title": ttl, "author": auth, "year": yr})
        print(f"Added ISBN: {isbn}, title: {ttl}, author {auth} and year {yr} to the database")
    db.commit()

if __name__ == "__main__":
    main()