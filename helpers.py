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


def timeline_info(playlists_ids):
    playlists = []

    # select all playlists from user
    for playlist in playlists_ids:
        playlists.append(playlist["playlist_id"])

    # retrieve proper information from playlists
    all_tracks = []
    for playlist_id in playlists:
        tracks = db.execute("SELECT * FROM tracks WHERE playlist_id= :playlist_id", playlist_id=playlist_id)
        for track in tracks:
            all_tracks.append(track)

    data = []

    for track in all_tracks:
        # making lists with important data for timeline
        track_info = []
        track_info.append(db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=track["added_by"]))
        track_info.append(youtube_api(track["link"]))
        track_info.append(track["time"])
        track_info.append(db.execute("SELECT playlist_name FROM playlists WHERE playlist_id = :playlist_id", playlist_id=track["playlist_id"]))
        track_info.append(track["link_desc"])
        track_info.append(db.execute("SELECT playlist_id FROM playlists WHERE playlist_id = :playlist_id", playlist_id=track["playlist_id"]))
        track_info.append(track["likes"])
        track_info.append(track["track_id"])

        # information for the liked/unliked button
        if check_liked(session["user_id"], track["track_id"]):
            track_info.append("liked")
        else:
            track_info.append("unliked")

        # insert all the information from 1 track to data
        data.append(track_info)

    # most recent songs are at the top of timeline
    data.sort(key=lambda x: x[2], reverse=True)
    return data


def yt_playlist_profile(all_tracks, user_id):

    # adding list for all the songs with their information
    links = []

    # looping all the songs
    for track in all_tracks:

        # making empty lists for the important information of the song
        track_info = []

        # adding the important information of the song to the list
        track_info.append(db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=track["added_by"]))
        track_info.append(youtube_api(track["link"]))
        track_info.append(track["time"])
        track_info.append(track["link_desc"])
        track_info.append(track["track_id"])
        track_info.append(track["likes"])
        track_info.append(track["added_by"])

        # information for the liked/unliked button
        if check_liked(user_id, track["track_id"]):
           track_info.append("liked")
        else:
            track_info.append("unliked")

        # insert all the information from 1 track to data
        links.append(track_info)

    # most recent songs are at the top of playlist_profile
    links.sort(key=lambda x: x[2], reverse=True)

    return links

def userprofile(user_id):

    # selecting the liked tracks of the user
    liked_tracks = db.execute("SELECT track_id FROM users_likedtracks WHERE user_id = :user_id", user_id=user_id)

    # making lists
    links = []

    # looping all the liked tracks
    for track in liked_tracks:

        # making list to add the link info to
        link_info = []

        # selecting all the required information and adding it
        track_id = track["track_id"]
        info = db.execute("SELECT link, link_desc, added_by, playlist_id, time FROM tracks WHERE track_id = :track_id", track_id = track_id)
        link = youtube_api(info[0]["link"])
        link_info.append(link)
        link_info.append(info[0]["link_desc"])
        user_id = info[0]["added_by"]
        adder = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id = user_id)
        link_info.append(adder[0]["username"])
        playlist_id = info[0]["playlist_id"]
        playlist = db.execute("SELECT playlist_name FROM playlists WHERE playlist_id = :playlist_id", playlist_id = playlist_id)
        link_info.append(playlist[0]["playlist_name"])
        link_info.append(info[0]["time"])
        link_info.append(playlist_id)

        # adding the information of a song to the end list
        links.append(link_info)

    # sorting the list
    links.sort(key=lambda x: x[4], reverse=True)

    return links


def player_info(playlist_id):

    uploads = db.execute("SELECT link FROM tracks WHERE playlist_id = :playlist_id", playlist_id = playlist_id)
    all_links = []
    for upload in uploads:
        all_links.append(youtube_api(upload["link"]))

    return all_links

def delete_playlist(playlist_id):
    db.execute("DELETE FROM playlists WHERE playlist_id= :playlist_id", playlist_id = playlist_id)
    db.execute("DELETE FROM playlist_users WHERE playlist_id= :playlist_id", playlist_id = playlist_id)
    track_id = db.execute("SELECT track_id FROM tracks WHERE playlist_id= :playlist_id", playlist_id = playlist_id)
    for track in track_id:
        db.execute("DELETE FROM users_likedtracks WHERE track_id = :track_id", track_id = track["track_id"])
    db.execute("DELETE FROM tracks WHERE playlist_id= :playlist_id", playlist_id = playlist_id)

