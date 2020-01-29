# VibeCheck
Developed by:
* Bart van den Broek (12675407)
* Martijn Schuurhuis (12404780)
* Naomi Rood (12666866)
* Toon Flipse (12729728)

---
### Features
VibeCheck is a website that allows users to create collaborative playlists. Once users have registered for an account, they can create playlists and upload songs to playlists using a YouTube link. Users can follow each other's playlists by clicking a simple "follow" button. When a user follows a playlist, all songs uploaded to that playlist will appear on their timeline, starting with the most recently added.
When a song is uploaded to a playlist, the name of the uploader and the name of the playlist the song was uploaded to are both displayed right above the song. Both the name of the uploader and the name of the playlist are clickable, allowing the user to easily navigate to the user's profile or to the playlist.
A user's profile shows how many songs they've uploaded in total, how many playlists they're following and a list of songs they liked and from where.
The creator of a playlist is allowed to delete their own playlist if they wish to do so, which also automatically deletes all songs uploaded to that playlist. The uploader of individual songs is also allowed to delete their own uploads, but not anybody else's.

Of course, the most important feature is the "play" button, which is usable as soon as a playlist contains one or more songs. The play button gathers all uploaded songs and adds them to a YouTube player, which will automatically play all songs, starting with the oldest one. 

---
### Planning
Bart van den Broek: 
* Created general design & lay-out
* Created lay-out for all html pages
* Like/unlike & follow/unfollow functionality
* Upload / descriptions functionality
* Database protection
* **Implemented automatic player functionality**
* Implemented JQuery functionality
* "Quality assurance"

Martijn Schuurhuis:
* Created helper functions
* Developed function to prepare links for YouTube API
* Developed implementation of < iframe> functionality
* Implemented JavaScript to block buttons when form isn't filled in correctly
* Recorded productvideo

Naomi Rood:
* Created foundation for app.routes
* Developed function to send correct info to timeline / playlist profile
* Created some html templates
* Implemented delete functions

Toon Flipse:
* Implemented JavaScript to check whether username/ playlist names are available
* Implemented JavaScript to check username & password when user tries to log in
* Implemented Search functionality
---
### Repository lay-out
* Application.py contains most of the website's functionality, such as all app.routes and database executions.
* All html files used to allow the user to interact with the website can be found in the templates folder.
* Helpers.py contains some functions that require a lot of lines, making application.py look cluttered. Therefore they were put in the helpers file.
* The static folder contains the logo of the website and a css file which contains the designs of elements of the website.
* The Docs folder contains a screenshot from the website and this README file.

<!--stackedit_data:
eyJoaXN0b3J5IjpbMTgzNTA0NzcyMiwtMjYyNDQ3NDc2LC05OD
MyNzU0MDgsLTE1OTM3MTQzMTQsMTc3NTIwODQyMywtMjA3MzU0
Nzk3N119
-->