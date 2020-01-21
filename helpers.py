import requests
import urllib.parse
import os
from cs50 import SQL


from flask import redirect, render_template, request, session
from functools import wraps

def youtube_api(link):
    db = SQL("sqlite:///project.db")

    link = link.split("=")
    link = link[1].split("&")

    for item in link:

        return item


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

