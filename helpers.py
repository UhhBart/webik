import requests
import urllib.parse
import os
from cs50 import SQL


from flask import redirect, render_template, request, session
from functools import wraps

def youtube_api():
    db = SQL("sqlite:///project.db")

    # getting the link from the database
    link = db.execute("SELECT NUMMER FROM numbers_link WHERE id=:user_id")

    # only getting the key of the song (everything behind the /watch?v=)
    key = link.split("=")

    # adding the key into the database
    db.execute("INSERT into key  ")



    return None


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