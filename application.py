import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for, json
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, youtube_api, check_following, link_check, check_liked, timeline_info, yt_playlist_profile, userprofile, player_info, delete_playlist

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

        # existing_users = db.execute("SELECT username FROM users")
        # for username in existing_users:
        #     if username == existing_users  ["username"]:
        #         return render_template("apology.html", message="that username is already taken")

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

        # ensure the user put in old passwords
        if not request.form.get("old_password"):
            return render_template("apology.html", message="Please enter your old password")

        # ensure the user to put in new password and confirmation of the new passord
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

        # giving the user a message that the password is changed
        flash("Password changed!")
        return redirect("/timeline")

    else:
        return render_template("change_password.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # forget any user_id
    session.clear()

    # user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", message="must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", message="must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("apology.html", message="invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # redirect user to home page
        return redirect("/timeline")

    # user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # forget any user_id
    session.clear()

    # redirect user to login form
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


@app.route("/check_playlist", methods=["GET"])
def check_playlist():
    """Check playlistname availability"""

    # retrieve playlist name
    playlist_name = request.args.get("playlist")

    # check whether playlist name already in database
    DB = db.execute("SELECT playlist_name FROM playlists WHERE playlist_name=:playlist_name", playlist_name=playlist_name)

    # return false if playlist name already exists
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

    # checking the password
    if not check_password_hash(rows[0]["hash"], request.args.get("password")):
        return jsonify(False)
    else:
        return jsonify(True)

@app.route("/timeline")
@login_required
def timeline():
    """Show timeline with posts from playlists user is following"""

    # select all playlists the current user follows
    playlists_ids = db.execute("SELECT playlist_id FROM playlist_users WHERE user_id= :user_id", user_id=session["user_id"])

    name = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=session["user_id"])

    # get all the information for timeline
    data = timeline_info(playlists_ids)

    return render_template("timeline.html", data=data, name=name)

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html")

    elif request.method == "POST":
        return render_template("results.html")

@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Allow user to create new playlists"""
    if request.method == "POST":

        # put new playlist information into database
        db.execute("INSERT INTO playlists (playlist_name, description, creator_id) VALUES(:playlist_name, :description, :creator_id)", playlist_name=request.form.get("playlist"), description=request.form.get("description"), creator_id = session['user_id'])

        # select playlist_id
        playlist_id = db.execute("SELECT playlist_id FROM playlists WHERE playlist_name= :playlist_name", playlist_name=request.form.get("playlist"))
        playlist_id = playlist_id[0]["playlist_id"]

        # link creator to playlist in another tabel
        db.execute("INSERT INTO playlist_users (playlist_id, user_id) VALUES(:playlist_id, :user_id)", user_id=session["user_id"], playlist_id=playlist_id)

        flash("Playlist created!")
        return redirect(url_for("playlists"))

    else:
        return render_template("create.html")


@app.route("/playlist_profile")
@login_required
def playlist_profile():
    """Show playlist with all uploaded songs"""

    # getting the info for the playlist_profile
    user_id = session["user_id"]
    current_user = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id = user_id)

    # get playlist_id
    playlist_id = request.args.get("id")

    # select proper information from database about playlist
    playlist_info = db.execute("SELECT description, creator_id, playlist_name FROM playlists WHERE playlist_id = :playlist_id", playlist_id=playlist_id)
    description = playlist_info[0]["description"]
    creator_id = playlist_info[0]["creator_id"]
    playlist_name = playlist_info[0]["playlist_name"]

    # select proper information from database
    followers = db.execute("SELECT user_id FROM playlist_users WHERE playlist_id = :playlist_id", playlist_id=playlist_id)
    all_tracks = db.execute("SELECT added_by, link, time, link_desc, track_id, likes FROM tracks WHERE playlist_id= :playlist_id", playlist_id=playlist_id)

    links = yt_playlist_profile(all_tracks, user_id)

    # gives current information about button
    if check_following(playlist_id, user_id):
        button = "follow"
    else:
        button = "unfollow"

    return render_template("playlist_profile.html", id= playlist_id, links=links, description=description, playlist_name=playlist_name,
                                posts=len(all_tracks), followers=len(followers), current_user=current_user, button=button, user_id=user_id, creator_id=creator_id)

@app.route("/upload", methods=["GET", "POST"])
@login_required
def add_number():
    """Allow users to upload songs to playlist"""

    # create form with proper information for user to upload a track
    if request.method == "GET":

        # create a form with all playlists
        playlist_names = []
        playlists = db.execute("SELECT playlist_id FROM playlist_users WHERE user_id = :user_id", user_id=session["user_id"])

        for playlist in playlists:
            playlist_id = playlist["playlist_id"]
            playlist_names.append(db.execute("SELECT playlist_name FROM playlists WHERE playlist_id = :playlist_id", playlist_id=playlist_id))

        return render_template("upload.html", playlists=playlist_names)

    else:

        # retrieve proper information
        playlist = request.form.get("playlist")

        if not playlist:
            return render_template("apology.html", message = "you did not correctly specifiy to which playlist you'd like to upload.")

        link = request.form.get("link")

        if not link_check(link):
            return render_template("apology.html", message = "the link you posted doesn't seem to meet our requirements, try generating a link using the share feature on YouTube.")

        link_desc = request.form.get("link_desc")

        # add track to database
        playlist_id = db.execute("SELECT playlist_id FROM playlists WHERE playlist_name = :playlist_name", playlist_name=playlist)
        db.execute("INSERT INTO tracks (playlist_id, link, added_by, link_desc) VALUES(:playlist_id, :link, :added_by, :link_desc)",
                   playlist_id=playlist_id[0]["playlist_id"], link=link, added_by=session["user_id"], link_desc=link_desc)

        # inform user upload was succesful and redirect to timeline
        flash("Upload succesful!")
        return redirect("/timeline")


@app.route("/results")
def results():
    # shows the results based on the users input in search
    # return to a specific playlist profile, from here the user can follow this playlist, so returns to /playlist_profile
    return None


@app.route("/follow")
@login_required
def follow():
    """Allow users to follow playlists"""

    playlist_id = request.args.get("playlist_id")
    user_id = session["user_id"]

    if check_following(playlist_id, user_id):
        db.execute("DELETE FROM playlist_users WHERE playlist_id = :playlist_id AND user_id = :user_id", playlist_id=playlist_id, user_id=session["user_id"])
        return jsonify(False)

    else:
        db.execute("INSERT INTO playlist_users (user_id, playlist_id) VALUES(:user_id, :playlist_id)",
                   user_id=session["user_id"], playlist_id=playlist_id)
        return jsonify(True)

    return render_template("apology.html")

@app.route("/playlists")
@login_required
def playlists():
    """Allow users to view the playlists they're following"""

    #
    ids = []
    playlist_id = db.execute("SELECT playlist_id FROM playlist_users WHERE user_id = :user_id", user_id=session["user_id"])

    #???
    for playlist_id in playlist_id:
        test = []
        playlist_name = db.execute("SELECT playlist_name FROM playlists WHERE playlist_id = :playlist_id", playlist_id=playlist_id["playlist_id"])
        test.append(playlist_name[0]["playlist_name"])
        test.append(playlist_id)
        ids.append(test)

    return render_template("playlists.html", ids=ids, playlist_id=playlist_id)

@app.route("/profile", methods=["GET"])
def profile():
    """Allow users to view their own or somebody else's profile"""

    user = request.args.get("username")
    if user:
        user_id = (db.execute("SELECT user_id FROM users WHERE username = :username", username=user))[0]["user_id"]

    else:
        user_id = session["user_id"]

    name = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=user_id)
    uploads = db.execute("SELECT link FROM tracks WHERE added_by = :added_by", added_by=user_id)
    playlists = db.execute("SELECT playlist_id FROM playlist_users WHERE user_id = :user_id", user_id=user_id)

    links = userprofile(user_id)

    return render_template("profile.html", name=name, uploads=len(uploads), playlists=len(playlists), links=links)


@app.route("/deletesong")
@login_required
def deletesong():

    track_id = request.args.get("track_id")
    user_id = session["user_id"]
    uploader = db.execute("SELECT added_by FROM tracks WHERE track_id = :track_id", track_id=track_id)

    if int(user_id) == int(uploader[0]["added_by"]):
        db.execute("DELETE FROM tracks WHERE track_id= :track_id", track_id = track_id)
        db.execute("DELETE FROM users_likedtracks WHERE track_id = :track_id", track_id = track_id)
        return jsonify(True)

    else:
        return jsonify(False)

@app.route("/deleteplaylist")
@login_required
def deleteplaylist():

    playlist_id = request.args.get("playlist_id")
    user_id = session["user_id"]
    creator = db.execute("SELECT creator_id FROM playlists WHERE playlist_id = :playlist_id", playlist_id=playlist_id)

    if not user_id == creator[0]["creator_id"]:
        return render_template("apology.html", message = "you are not the creator of this playlist, therefore you're not allowed to delete it")

    delete_playlist(playlist_id)
    return redirect ("/playlists")

@app.route("/upvote")
@login_required
def upvote():
    track_id = request.args.get("track_id")
    user_id = session["user_id"]

    if check_liked(user_id, track_id):
        db.execute("DELETE FROM users_likedtracks WHERE track_id = :track_id AND user_id= :user_id", track_id=track_id, user_id=user_id)
        db.execute("UPDATE tracks SET likes = likes - 1 WHERE track_id = :track_id", track_id=track_id)
        return jsonify(False)
    else:
        db.execute("INSERT INTO users_likedtracks (track_id, user_id) VALUES (:track_id, :user_id)", track_id=track_id, user_id=user_id)
        db.execute("UPDATE tracks SET likes = likes + 1 WHERE track_id = :track_id", track_id=track_id)
        return jsonify(True)


@app.route("/player", methods=["GET"])
def player():

    playlist_id = request.args.get("playlist_id")
    videos = (player_info(playlist_id))

    return render_template("player.html", videos = videos)