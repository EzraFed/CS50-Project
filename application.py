from helpers import apology
import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
# https://stackoverflow.com/questions/11710469/how-to-get-python-to-display-current-time-eastern
from pytz import timezone
est = timezone('EST')


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///documents.db")


@app.route("/", methods=["GET", "POST"])
def home():
    """Homepage"""
    if (request.method == "POST"):
        # store the document type in session['category']
        session['category'] = request.form.get("category")
        # send user to list of documents related to the category they chose
        return redirect("/directory")
    else:
        # declare an empty list, called editable, in session if it has not already been done.
        if (not 'editable' in session):
            session['editable'] = []
        return render_template("home.html")


@app.route("/directory", methods=["GET", "POST"])
def directory():
    """Directory"""
    if (request.method == "POST"):
        # name stores the name of the selected file
        session['name'] = request.form.get("doc")
        # get the password, if it exists
        password = db.execute("SELECT password FROM documents WHERE name = :name", name=session['name'])
        # check if password is blank
        if (check_password_hash(password[0]['password'], "")):
            # if password is blank, immediately make the file editable
            if (not session['name'] in session['editable']):
                session['editable'].append(session['name'])
        return redirect("/document")
    else:
        # select all documents for the chosen category
        documents = db.execute("SELECT name FROM documents WHERE category = :category ORDER BY date DESC",
                               category=session['category'])
        # reformat name of documents to exclude .txt
        for document in documents:
            # https://stackoverflow.com/questions/1798465/python-remove-last-3-characters-of-a-string
            document['name'] = document['name'][:-4]
        # render the list of documents
        return render_template("directory.html", documents=documents)


@app.route("/document", methods=["GET", "POST"])
def document():
    if (request.method == "POST"):
        # check if the user may edit the document
        if (session['name'] in session['editable']):
            # open the relevant document in append mode
            # https://www.w3schools.com/python/python_file_write.asp
            file = open(session['name'], "a")
            # delete the contents of the document by making it 0 bytes
            # https://stackoverflow.com/questions/2769061/how-to-erase-the-file-contents-of-text-file-in-python
            file.truncate(0)
            file.close()
            # reopen the file in writing mode
            file = open(session['name'], "w")
            # write the user's new content into the file
            file.write(request.form.get("textarea"))
            return redirect("/document")
        else:
            return redirect("/login")
    else:
        # read the contents of the document into the interface
        # https://www.w3schools.com/python/python_file_open.asp
        file = open(session['name'], "r")
        # check if user can edit the document
        if (session['name'] in session['editable']):
            return render_template("document.html", document=file.read(), editable=True)
        else:
            # if the user cannot edit the document, render the view-only page
            return render_template("document.html", document=file.read(), editable=False)


@app.route("/login", methods=["GET", "POST"])
def login():
    if (request.method == "POST"):
        # create variable password which holds users password input
        password = request.form.get("password")
        # get password of the document
        check = db.execute("SELECT password FROM documents WHERE name = :name", name=session['name'])
        # check if inputed password matches correct password
        if (check_password_hash(check[0]['password'], password)):
            # make the document editable
            session['editable'].append(session['name'])
            # redirect to /document page
            return redirect("/document")
        else:
            return apology("Incorrect password", 403)
    else:
        return render_template("login.html")


@app.route("/new", methods=["GET", "POST"])
def new():
    if (request.method == "POST"):
        # Set session['name'] to the name of the document (with .txt appended)
        session['name'] = request.form.get("name")
        session['name'] = session['name'] + ".txt"
        # check if name is already the name of someone else's document
        current = db.execute("SELECT COUNT(name) FROM documents WHERE name = :name", name=session['name'])
        if int(current[0]['COUNT(name)']) > 0:
            return apology("That document name already exists.")
        else:
            # set password to the password entered by the user
            password = request.form.get("password")
            # make the created document editable
            session['editable'].append(session['name'])
            # add the new document to the SQL database
            db.execute("INSERT INTO documents (name, password, category, date) VALUES (:name, :password, :category, :date)",
                       name=session['name'], password=generate_password_hash(password), category=session['category'], date=datetime.now(est))
            # https://www.w3schools.com/python/python_file_handling.asp
            # create the actual file
            file = open(session['name'], "x")
            file.close()
            # redirect to the document page with the new document
            return redirect("/document")
    else:
        return render_template("new.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
