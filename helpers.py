import requests
import urllib.parse
import os
from cs50 import SQL


from flask import redirect, render_template, request, session
from functools import wraps

def youtube_api():
    db = SQL("sqlite:///project.db")

    # getting the link from the database
    link = db.execute("SELECT link FROM tracks")

    list1 = list()
    list2 = list()
    for i in link:
        list1.append(list(i.values()))

    # only getting the key of the song (everything behind the /watch?v= and before &list if song is in playlist)
    for i in list1:
        for j in i:
            youtube_key = j.split("=")
            youtube_key = youtube_key[1].split("&")
            list2.append(youtube_key)

    return list2


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