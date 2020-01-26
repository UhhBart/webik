import requests
import urllib.parse
import os
from cs50 import SQL


from flask import redirect, render_template, request, session
from functools import wraps
db = SQL("sqlite:///project.db")

def youtube_api(link):

    if "=" in link:
        link = link.split("=")
        link = link[1].split("&")

        for item in link:
            return item
    else:
        link = link.split("e/")
        link = link[1].split("?")
        for item in link:
            return item




def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def check_following(playlist_id, user_id):
    """Functions that checks if playlist is followed by user"""

    check_follow = db.execute("SELECT user_id FROM playlist_users WHERE playlist_id = :playlist_id",
                              playlist_id=playlist_id)
    for i in check_follow:
        if i["user_id"] == user_id:
            return True

def link_check(link):
    if "youtube.com/watch?v=" in link:
        return 1
    elif "youtu.be/" in link:
        return 2
    else:
        return False

def check_liked(user_id, track_id):

    check_liked = db.execute("SELECT user_id FROM users_likedtracks WHERE track_id = :track_id", track_id=track_id)

    for i in check_liked:
        if i["user_id"] == user_id:
            return True


def yttest(playlists,data,rows):

    for link in rows:
        data1 = []
        data1.append(db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=link["added_by"]))
        youtube = link["link"]

        # making lists with important data for timeline
        data1.append(youtube_api(youtube))
        data1.append(link["time"])
        data1.append(db.execute("SELECT playlist_name FROM playlists WHERE playlist_id = :playlist_id", playlist_id=link["playlist_id"]))
        data1.append(link["link_desc"])
        data1.append(db.execute("SELECT playlist_id FROM playlists WHERE playlist_id = :playlist_id", playlist_id=link["playlist_id"]))
        data1.append(link["likes"])
        data1.append(link["track_id"])

        if check_liked(session["user_id"], link["track_id"]):
            data1.append("liked")
        else:
            data1.append("unliked")
        data.append(data1)

        # most recent songs are at the top of timeline
    data.sort(key=lambda x: x[2], reverse=True)
    return data