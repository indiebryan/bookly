import os
import requests

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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


@app.route("/")
def index():
	key = 'atf1iuT5jA46CkYZ7Wpzfw'
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": "9781632168146"})
	return render_template("index.html", val=str(res.json()['books'][0]['work_ratings_count']))

@app.route("/register")
def register():
	return render_template("register.html")