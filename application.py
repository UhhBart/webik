import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
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
        password = db.execute("SELECT hash FROM users WHERE user_id = :user_id", user_id=session["user_id"])

        # ensure old password is correct
        if len(password) != 1 or not check_password_hash(password[0]["hash"], request.form.get("old_password")):
            return render_template("apology.html", message = "Incorrect password" )

        # change user's password
        hash = generate_password_hash(request.form.get("new_confirmation"), method='pbkdf2:sha256', salt_length=8)
        db.execute("UPDATE users SET hash = :hash WHERE user_id = :user_id",
                   user_id=session["user_id"], hash=hash)

        flash ("Password changed!")
        return redirect ("/timeline")

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

@app.route("/timeline")
@login_required
def timeline():

# shows the homepage for logged in users
# shows playlists  the user follows(with added number)

# returns to /create
# returns to /group_profile from all the groups that the user follows
    groups_ids = db.execute ("SELECT group_id FROM group_users WHERE user_id= :user_id", user_id = session["user_id"])
    name = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id = session["user_id"])
    # select all groups from current_user
    groups =[]
    for group in groups_ids:
        groups.append(group["group_id"])

    data =[]
    for group_id in groups:
        rows = db.execute("SELECT group_id, added_by, link, time, link_desc FROM tracks WHERE group_id= :group_id", group_id = group_id)

        print(rows)
        for link in rows:
            data1 = []
            #data1.append(link["group_id"])
            data1.append(db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id = link["added_by"]))
            youtube = link["link"]
            #moet hier door de youtube_api gaan
            data1.append(youtube_api(youtube))
            data1.append(link["time"])
            data1.append(db.execute("SELECT group_name FROM groups WHERE group_id = :group_id", group_id = link["group_id"]))
            data1.append(link["link_desc"])
            data.append(data1)
    # most recent songs are at the top of timeline
    data.sort(key=lambda x: x[2], reverse = True)
    return render_template("timeline.html", data=data, name=name)


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

        return redirect(url_for('playlists'))


    else:
        return render_template("create.html")

@app.route("/group_profile")
def group_profile():
# shows the playlist of that group
# add numbers if you are member of that group
# shows the users of that group (short description)
# includes a button for following a group

#return to /add_number

    # getting the info for the group_profile

    # aangeleverd
    group_name = request.args.get("name")

    description = db.execute("SELECT description FROM groups WHERE group_name= :group_name", group_name = group_name)
    group_id = db.execute("SELECT group_id FROM groups WHERE group_name= :group_name", group_name = group_name)
    for group in group_id:
        group_id = group["group_id"]

        followers = db.execute("SELECT user_id FROM group_users WHERE group_id = :group_id", group_id = group_id)

        rows = db.execute("SELECT added_by, link, time, link_desc FROM tracks WHERE group_id= :group_id", group_id = group_id)

        links =[]
        for link in rows:
            data1 = []

            data1.append(db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id = link["added_by"]))
            youtube = link["link"]
            #moet hier door de youtube_api gaan
            data1.append(youtube_api(youtube))
            data1.append(link["time"])
            data1.append(link["link_desc"])
            links.append(data1)

        return render_template("group_profile.html", links=links, description=description, group_name = group_name, posts = len(rows), followers = len(followers))

@app.route("/upload", methods=["GET", "POST"])
@login_required
def add_number():
# add a number to a playlist

    if request.method == "GET":
        group_names = []
        groups = db.execute("SELECT group_id FROM group_users WHERE user_id = :user_id", user_id = session["user_id"])
        for group in groups:
            group_id = group["group_id"]
            group_names.append(db.execute("SELECT group_name FROM groups WHERE group_id = :group_id", group_id = group_id))
        return render_template("upload.html", groups = group_names)

    elif request.method == "POST":
        group = request.form.get("group")
        link = request.form.get("link")
        link_desc = request.form.get("link_desc")

        group_id = db.execute("SELECT group_id FROM groups WHERE group_name = :group_name", group_name = group)
        db.execute("INSERT INTO tracks (group_id, link, added_by, link_desc) VALUES(:group_id, :link, :added_by, :link_desc)", group_id = group_id[0]["group_id"], link = link, added_by = session["user_id"], link_desc = link_desc)
        flash("Upload succesful!")
        return redirect("/timeline")

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

@app.route("/follow", methods = ["POST"])
@login_required
def follow():
    group_name = request.form.get("follow")
    group_id = db.execute("SELECT group_id FROM groups WHERE group_name = :group_name", group_name = group_name)
    now_following = db.execute("INSERT INTO group_users (user_id, group_id) VALUES(:user_id, :group_id)", user_id = session["user_id"], group_id = group_id[0]["group_id"])
    if not now_following:
        return render_template("apology.html")
    return jsonify(True)

@app.route("/playlists")
@login_required
def playlists():
    ids = []
    playlist_id = db.execute("SELECT group_id FROM group_users WHERE user_id = :user_id", user_id = session["user_id"])
    for i in range(len(playlist_id)):
        #ids.append(playlist_id[i]["group_id"])
        playlist_name = db.execute("SELECT group_name FROM groups WHERE group_id = :group_id", group_id = playlist_id[i]["group_id"])
        ids.append(playlist_name[0]["group_name"])
    return render_template("playlists.html", ids = ids)

@app.route("/profile", methods = ["GET"])

def profile():
    return render_template("profile.html")

# # copied from finance
# def errorhandler(e):
#     """Handle error"""
#     if not isinstance(e, HTTPException):
#         e = InternalServerError()
#         return render_template("apology.html", message = "" )(e.name, e.code)


# # Listen for errors
# for code in default_exceptions:
#     app.errorhandler(code)(errorhandler)
