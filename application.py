import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, youtube_api

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
db = SQL("sqlite:///project.db")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        password = request.form.get("password")
        username = request.form.get("username")
        confirm_password = request.form.get("confirm_password")


        # make sure the user put in a username
        if not username:
            return render_template("apology.html", message = "Please enter your new username." )

        # make sure the user put in a password
        elif not password:
            return render_template("apology.html", message = "Please enter your new password.")

        # make sure password is at least 8 characters
        elif len(password) < 8:
            return render_template("apology.html", message = "Make sure password is at least 8 characters" )

        # make sure the password and the repeated password match
        elif not password == confirm_password:
            return render_template("apology.html", message = "Your passwords don't match, please try again" )

        # add the new user's account to the databse
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                   username=request.form.get("username"), hash=generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8))

        return redirect("/timeline")

    else:
        return render_template("register.html")


@app.route("/change_password", methods = ["POST", "GET"])
@login_required
def change_password():

    if request.method == "POST":

        # ensure the user put in old and new passwords
        if not request.form.get("old_password"):
            return render_template("apology.html", message = "Please enter your old password" )

        elif not request.form.get("new_password"):
            return render_template("apology.html", message = "Please enter your new password" )

        elif not request.form.get("new_confirmation"):
            return render_template("apology.html", message = "Please enter your new password" )

        # ensure the new passwords match
        if not request.form.get("new_password") == request.form.get("new_confirmation"):
            return render_template("apology.html", message = "Passwords don't match" )

        # retrieve user's old password
        password = db.execute("SELECT hash FROM users WHERE id = :id", id=session["user_id"])

        # ensure old password is correct
        if len(password) != 1 or not check_password_hash(password[0]["hash"], request.form.get("old_password")):
            return render_template("apology.html", message = "Incorrect password" )

        # change user's password
        hash = generate_password_hash(request.form.get("new_confirmation"), method='pbkdf2:sha256', salt_length=8)
        db.execute("UPDATE users SET hash = :hash WHERE id = :id",
                   id=session["user_id"], hash=hash)

        flash ("Password changed!")
        return redirect ("/")

    else:
        return render_template("change_password.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", message = "must provide username" )

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", message = "must provide password" )

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("apology.html", message = "invalid username and/or password" )

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/timeline")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/", methods=["GET", "POST"])
def general_homepage():
# shows the homepage when users aren’t logged in
# return naar log in and register
    if request.method == "POST":
        if request.form['button'] == 'register':
            return render_template("register.html")
        else:
            return render_template("login.html")


    else:
        return render_template("general_homepage.html")

@app.route("/timeline", methods=["GET", "POST"])
@login_required
def timeline():

# shows the homepage for logged in users
# shows playlists  the user follows(with added number)

# returns to /create
# returns to /group_profile from all the groups that the user follows

    if request.method == "POST":
        if request.form['button'] == 'create':
            return render_template("create.html")

    else:

        return render_template("timeline.html")

@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
# creating a new group/playlist
# return group profile

    if request.method == "POST":
        #set group into groups
        db.execute("INSERT INTO groups (group_name, description) VALUES(:group_name, :description)",
                   group_name=request.form.get("playlist"),
                   description=request.form.get("description"))

        # link user en group
        group_id = db.execute("SELECT group_id FROM groups WHERE group_name= :group_name", group_name = request.form.get("playlist"))
        for group in group_id:
            gr_id = group["group_id"]

        db.execute("INSERT INTO group_users (group_id, user_id) VALUES(:group_id, :user_id)",
                    user_id = session["user_id"], \
                    group_id = gr_id)


        #bestaat nog niet maar is voor de sier
        return render_template("group_profile.html")




    else:
        return render_template("create.html")

@app.route("/group_profile")
def group_profile():
# shows the playlist of that group
# add numbers if you are member of that group
# shows the users of that group (short description)
# includes a button for following a group

#return to /add_number

    # is informatie nodig van de groep waarop is geklikt
    # group_information = db.execute("SELECT name, description FROM groups WHERE)
    return render_template("group_profile.html")

@app.route("/add_number")
@login_required
def add_number():
# add a number to a playlist
# only when that user is a member of that group
    return None

@app.route("/search")
def search():
# this is a searchpage to look for new groups/ playlists
# based on a users input
# return to results
    return None

@app.route("/results")
def results():
# shows the results based on the users input in search
# return to a specific group profile, from here the user can follow this group, so returns to /group_profile
    return None

@app.route("/follow", methods = ["GET"])
def follow():
#information that user follows a group in database
    return None

# # copied from finance
# def errorhandler(e):
#     """Handle error"""
#     if not isinstance(e, HTTPException):
#         e = InternalServerError()
#         return render_template("apology.html", message = "" )(e.name, e.code)


# # Listen for errors
# for code in default_exceptions:
#     app.errorhandler(code)(errorhandler)
