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

# Get API key for goodreads from local file
gr_file = open("goodreads.key", "r")
gr_key = gr_file.read()

# TODO: Handle user login auth
@app.route("/", methods=["GET", "POST"])
def index():
	if request.method == "POST":
		_username = request.form.get("username")
		_password = request.form.get("password")
		valid = db.execute("SELECT username FROM users WHERE username = :_username AND password = :_password",
			{"_username": _username, "_password": _password}).fetchone()
		if valid is None:
			return render_template("error.html", message="Incorrect username or password")
		else:
			session["username"] = _username
			return render_template("index.html", val=valid, user=session["username"])

	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": gr_key, "isbns": "9781632168146"})
	return render_template("index.html", val=str(res.json()['books'][0]['work_ratings_count']) + 'aa', user=session["username"])

@app.route("/flights")
def flights():
	flights = db.execute("SELECT origin, destination FROM flights").fetchall()
	return render_template("flights.html", flights=flights)

@app.route("/login")
def login():
	return render_template("login.html")

@app.route("/logout")
def logout():
	session["username"] = ""
	return render_template("index.html", user=session["username"])


@app.route("/register")
def register():
	return render_template("register.html")

@app.route("/hello", methods=["POST"])
def hello():
	username = request.form.get("username")
	password = request.form.get("password")
	try:
		db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": password})
		db.commit();
		return render_template("hello.html", username=username)
	except:
		return render_template("error.html", message="Username already exists, probably.")

@app.route("/books", methods=["GET", "POST"])
def books():
	if session.get("book_list") is None:
		session["book_list"] = []

	if request.method == "POST":
		session["book_list"].append(request.form.get("book"))
	return render_template("books.html", book_list=session["book_list"])