import requests
import urllib.parse
import os
from cs50 import SQL


from flask import redirect, render_template, request, session
from functools import wraps

def youtube_api():
    db = SQL("sqlite:///project.db")

    # getting the link from the database
    link = db.execute("SELECT link FROM tracks WHERE id=:user_id")

    # only getting the key of the song (everything behind the /watch?v= and before &list if song is in playlist)
    youtube_key = link.split("=")
    youtube_key = youtube_key[1].split("&")

    # adding the key into the database
    # db.execute("INSERT INTO groups (youtube_key) VALUES (:youtube_key)")

    return youtube_key[0]


    #https://www.youtube.com/watch?v=4fndeDfaWCg     <-- check deze banger

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