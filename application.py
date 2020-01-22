import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, youtube_api, check_following, link_check

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

        # initialize variables
        password = request.form.get("password")
        username = request.form.get("username")
        confirm_password = request.form.get("confirmation")

        # make sure the user put in a username
        if not username:
            return render_template("apology.html", message="Please enter your new username.")

        # make sure the user put in a password
        elif not password:
            return render_template("apology.html", message="Please enter your new password.")

        # make sure password is at least 8 characters
        elif len(password) < 8:
            return render_template("apology.html", message="Make sure password is at least 8 characters")

        # make sure the password and the repeated password match
        elif not password == confirm_password:
            return render_template("apology.html", message="Your passwords don't match, please try again")

        # add the new user's account to the databse
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                   username=request.form.get("username"), hash=generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8))

        return redirect("/timeline")

    else:
        return render_template("register.html")


@app.route("/change_password", methods=["POST", "GET"])
@login_required
def change_password():

    if request.method == "POST":

        # ensure the user put in old and new passwords
        if not request.form.get("old_password"):
            return render_template("apology.html", message="Please enter your old password")

        elif not request.form.get("new_password"):
            return render_template("apology.html", message="Please enter your new password")

        elif not request.form.get("new_confirmation"):
            return render_template("apology.html", message="Please enter your new password")

        # ensure the new passwords match
        if not request.form.get("new_password") == request.form.get("new_confirmation"):
            return render_template("apology.html", message="Passwords don't match")

        # retrieve user's old password
        password = db.execute("SELECT hash FROM users WHERE user_id = :user_id", user_id=session["user_id"])

        # ensure old password is correct
        if len(password) != 1 or not check_password_hash(password[0]["hash"], request.form.get("old_password")):
            return render_template("apology.html", message="Incorrect password")

        # change user's password
        hash = generate_password_hash(request.form.get("new_confirmation"), method='pbkdf2:sha256', salt_length=8)
        db.execute("UPDATE users SET hash = :hash WHERE user_id = :user_id",
                   user_id=session["user_id"], hash=hash)

        flash("Password changed!")
        return redirect("/timeline")

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
            return render_template("apology.html", message="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", message="must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("apology.html", message="invalid username and/or password")

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
    """Guide user to homepage"""

    if request.method == "POST":
        if request.form['button'] == 'register':
            return render_template("register.html")

        else:
            return render_template("login.html")

    else:
        return render_template("general_homepage.html")


@app.route("/check", methods=["GET"])
def check():
    """Check username availability"""

    # retrieve username
    username = request.args.get("username")

    # check whether username already in database
    usernames = db.execute("SELECT * FROM users WHERE username=:username", username=username)

    # return false if username already exists
    if len(usernames) != 0:
        return jsonify(False)

    return jsonify(True)


@app.route("/check_group", methods=["GET"])
def check_group():
    """Check groupname availability"""

    # retrieve group name
    group_name = request.args.get("playlist")

    # check whether group name already in database
    DB = db.execute("SELECT group_name FROM groups WHERE group_name=:group_name", group_name=group_name)

    # return false if group name already exists
    if len(DB) != 0:
        return jsonify(False)

    return jsonify(True)

@app.route("/check_login_username", methods=["GET"])
def check_login_username():
    """Check username availability"""
    # Query database for username


    rows = db.execute("SELECT * FROM users WHERE username = :username",
                      username=request.args.get("username"))

    # Ensure username exists and password is correct
    if len(rows) != 1:
        return jsonify(False)

    else:
        return jsonify(True)

@app.route("/check_login_password", methods=["GET"])
def check_login_password():
    """Check username availability"""


    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                      username=request.args.get("username"))
    if not check_password_hash(rows[0]["hash"], request.args.get("password")):
        return jsonify(False)
    else:
        return jsonify(True)


@app.route("/timeline")
@login_required
def timeline():
    """Show timeline with posts from playlists user is following"""

    # retrieve playlists user is following from database
    groups_ids = db.execute("SELECT group_id FROM group_users WHERE user_id= :user_id", user_id=session["user_id"])
    name = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=session["user_id"])

    # select all playlist from user
    groups = []
    for group in groups_ids:
        groups.append(group["group_id"])

    # retrieve proper information from playlists
    data = []
    for group_id in groups:
        rows = db.execute("SELECT group_id, added_by, link, time, link_desc FROM tracks WHERE group_id= :group_id", group_id=group_id)

        #???
        for link in rows:
            data1 = []
            data1.append(db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=link["added_by"]))
            youtube = link["link"]

            # moet hier door de youtube_api gaan
            data1.append(youtube_api(youtube))
            data1.append(link["time"])
            data1.append(db.execute("SELECT group_name FROM groups WHERE group_id = :group_id", group_id=link["group_id"]))
            data1.append(link["link_desc"])
            data.append(data1)
    # most recent songs are at the top of timeline
    data.sort(key=lambda x: x[2], reverse=True)
    return render_template("timeline.html", data=data, name=name)


@app.route("/search", methods=["GET"])
def search():
    new = []
    # searchInput = request.args.get("search")
    # print(searchInput, request.args.get("search"))
    groups = db.execute("SELECT group_name FROM groups")
    print(groups, (request.args.get("q")))
    # return render_template("/general_homepage.html", groups=groups)
    for playlist in groups:
        playlist["group_name"] = playlist["group_name"].lower()
        print(playlist["group_name"].startswith(request.args.get("q")))
        if playlist["group_name"].startswith(request.args.get('q')):
            new.append(playlist["group_name"])

    print(new)
    return new


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Allow user to create new playlists"""
    if request.method == "POST":

        # put new playlist information into database
        db.execute("INSERT INTO groups (group_name, description, creator_id) VALUES(:group_name, :description, :creator_id)",
                   group_name=request.form.get("playlist"),
                   description=request.form.get("description"),
                   creator_id = session['user_id'])

        # link creator to group
        group_id = db.execute("SELECT group_id FROM groups WHERE group_name= :group_name", group_name=request.form.get("playlist"))

        # ???
        for group in group_id:
            gr_id = group["group_id"]

        db.execute("INSERT INTO group_users (group_id, user_id) VALUES(:group_id, :user_id)",
                   user_id=session["user_id"],
                   group_id=gr_id)

        return redirect(url_for("playlists"))

    else:
        return render_template("create.html")


@app.route("/group_profile")
@login_required
def group_profile():
    """Show playlist with all uploaded songs"""

    current_user = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id = session["user_id"])

    # getting the info for the group_profile

    # aangeleverd
    group_name = request.args.get("name")
    user_id = session["user_id"]

    # select proper information from database
    description = db.execute("SELECT description FROM groups WHERE group_name= :group_name", group_name=group_name)
    group_id = db.execute("SELECT group_id FROM groups WHERE group_name= :group_name", group_name=group_name)


    creator_id = db.execute("SELECT creator_id FROM groups WHERE group_name= :group_name", group_name=group_name)
    for id in creator_id:
        creator_id = id["creator_id"]

    user_id = session["user_id"]
    #???
    for group in group_id:
        group_id = group["group_id"]

        # select proper information from database
        followers = db.execute("SELECT user_id FROM group_users WHERE group_id = :group_id", group_id=group_id)
        rows = db.execute("SELECT added_by, link, time, link_desc, track_id FROM tracks WHERE group_id= :group_id", group_id=group_id)


        #???
        links = []
        for link in rows:
            data1 = []

            data1.append(db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=link["added_by"]))
            youtube = link["link"]
            # ???
            data1.append(youtube_api(youtube))
            data1.append(link["time"], link["link_desc"], link["track_id"])
            links.append(data1)

        # most recent songs are at the top of group_profile
        links.sort(key=lambda x: x[2], reverse=True)

        if check_following(group_id, user_id):
            button = "follow"
        else:
            button = "unfollow"

        return render_template("group_profile.html", id= group_id, links=links, description=description, group_name=group_name,
                                posts=len(rows), followers=len(followers), current_user=current_user, button=button, user_id=user_id, creator_id=creator_id)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def add_number():
    """Allow users to upload songs to playlist"""

    # create form with proper information for user to upload a track
    if request.method == "GET":
        group_names = []
        groups = db.execute("SELECT group_id FROM group_users WHERE user_id = :user_id", user_id=session["user_id"])

        for group in groups:
            group_id = group["group_id"]
            group_names.append(db.execute("SELECT group_name FROM groups WHERE group_id = :group_id", group_id=group_id))

        return render_template("upload.html", groups=group_names)

    elif request.method == "POST":

        # retrieve proper information
        group = request.form.get("group")
        link = request.form.get("link")

        if not link_check(link):
            return render_template("apology.html", message = "HOW DARE YOU")

        link_desc = request.form.get("link_desc")

        # add track to database
        group_id = db.execute("SELECT group_id FROM groups WHERE group_name = :group_name", group_name=group)
        db.execute("INSERT INTO tracks (group_id, link, added_by, link_desc) VALUES(:group_id, :link, :added_by, :link_desc)",
                   group_id=group_id[0]["group_id"], link=link, added_by=session["user_id"], link_desc=link_desc)

        # inform user upload was succesful and redirect to timeline
        flash("Upload succesful!")
        return redirect("/timeline")


@app.route("/results")
def results():
    # shows the results based on the users input in search
    # return to a specific group profile, from here the user can follow this group, so returns to /group_profile
    return None


@app.route("/follow")
@login_required
def follow():
    """Allow users to follow playlists"""

    group_id = request.args.get("name")
    user_id = session["user_id"]

    if check_following(group_id, user_id):
        db.execute("DELETE FROM group_users WHERE group_id = :group_id AND user_id = :user_id", group_id=group_id, user_id=session["user_id"])
        return jsonify("Unfollowed")

    else:
        db.execute("INSERT INTO group_users (user_id, group_id) VALUES(:user_id, :group_id)",
                   user_id=session["user_id"], group_id=group_id)
        return jsonify("Followed")

    return render_template("apology.html")

@app.route("/playlists")
@login_required
def playlists():
    """Allow users to view the playlists they're following"""

    #???
    ids = []
    playlist_id = db.execute("SELECT group_id FROM group_users WHERE user_id = :user_id", user_id=session["user_id"])

    #???
    for i in range(len(playlist_id)):
        playlist_name = db.execute("SELECT group_name FROM groups WHERE group_id = :group_id", group_id=playlist_id[i]["group_id"])
        ids.append(playlist_name[0]["group_name"])

    return render_template("playlists.html", ids=ids)


@app.route("/profile", methods=["GET"])
def profile():
    name = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=session["user_id"])
    return render_template("profile.html", name=name)


@app.route("/deletesong")
@login_required
def deletesong():

    track_id = request.args.get("track_id")

    db.execute("DELETE FROM tracks WHERE track_id= :track_id", track_id = track_id)


@app.route("/deleteplaylist")
@login_required
def deleteplaylist():

    group_id = request.args.get("group_id")

    db.execute("DELETE FROM groups WHERE group_id= :group_id", group_id = group_id)
    # er moet nog meer worden verwijderd maar dit is de basis


# # copied from finance
# def errorhandler(e):
#     """Handle error"""
#     if not isinstance(e, HTTPException):
#         e = InternalServerError()
#         return render_template("apology.html", message = "" )(e.name, e.code)


# # Listen for errors
# for code in default_exceptions:
#     app.errorhandler(code)(errorhandler)
