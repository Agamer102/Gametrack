# Gametrack
#### Video Demo:  removed
## Overview
This is a simple flask web app for a server to keep track of users games.
It allows for users to add any game currently on Steam or VNDB or alternatively
to add their own custom games. 

## Compiling

* Create a virtual environment by running
 * python3 -m venv .venv
 * . .venv/bin/activate (on Mac/Linux)
 * .venv\Scripts\activate (on Windows)
* Run: pip install build
* Run: python -m build --wheel

## Installation

* Run: pip install (name of the file that was created)
* Create a config.py file in the instance directory (.venv/var/gametrack-instance)
* Generate a secure key by running python -c 'import secrets; print(secrets.token_hex())'
* Set SECRET_KEY = 'value you generated'
* Get a Steam API key from <https://steamcommunity.com/dev/apikey>
* Set STEAM_API_KEY = 'your steam api key'

## Usage

* To initialize the database run: flask --app gametrack init-db
* To test the server, run: flask run --app gametrack --debug
* For production, you call the create_app() function and give its' return value to the server
* For pythonanywhere use the following code in the wgsi configuration file:

import sys

path = '/home/{your-username}/.virtualenvs/my-virtualenv/lib/python3.10/site-packages/gametrack'
if path not in sys.path:
    sys.path.append(path)

from gametrack import create_app # noqa

application = create_app()

## Contributing

I'll keep working on this on my free time.
If you want to see the site visit <https://agamer102.pythonanywhere.com/>

CS50X final project of Adithya Dissanayake

## Description

### Goal
My main goal with this project was to create a website that I'd personally want to use. My previous project had a similar
purpose but I found that using it was far too annoying as it only supported a CLI. Hence for this project, I decided to
use a web app instead, and also incorporate integration with VNDB, which I couldn't with my previous project. With the
intention of also allowing several other users to also use this site, I used a login-based method.

### Design
I started with completing the tutorial on <https://flask.palletsprojects.com/en/3.0.x/tutorial/> as I wanted a more
standardised design for my web app, and used the frame I build using that tutorial to build my site on. This also had
instructions on how to do unit tests for the app, but due to time constraints I decided to only include the pre-written
tests.

### Steam library Integration
This was a feature that was also present in my previous project, I implemented it in mostly the same way here, by using
the Steam API with my personal Steam API key. In addition, I decided to keep track of which games were added via Steam
and to not delete them, but rather mark them as deleted to avoid them showing up again when a user deleted a game.

### Steam/VNDB Integration
Initially, I used the Steam and VNDB APIs to query for games. This worked fine mostly, but had the restriction of only
being able to add games via their Steam and VNDB ids. I was willing to bear with this, but because of how difficult I
found the VNDB api to work with, I decided instead to download their database dump, and use that to formulate my database.
For consistency I also decided to do the same with Steam using the GetAppList method on their api. This had the added
benefit that users were now able to just search for games on the site by their names. I also added code in library.py so
that the Steam and VNDB queries were joined if they were the same game.

### Custom Games
This was a feature present in the first version of my app, which I then removed because I felt that it was unnecessary as
I was under the impression there would be almost no popular games not on Steam or VNDB. I was proven wrong in the first alpha
test I ran, with the help of some friends, when a user found that some very popular games like Minecraft and Valorant were
missing (along with several more bugs relating to users with empty Steam libraries and accessing offline playtime). This
prompted me to add support for adding games manually, if the user cannot find the game they want in the site. However, as
I didn't want another API integration at this point, I decided to make it the user's responsibility to find a suitable 
image.

### The Database
I implemented a total of 7 tables for the database, 3 of which were for tracking the games on Steam, VNDB and their
relationship. In hindsight, it might have been more prudent to simply join all these tables into one, or alternatively
use it as a separate database entirely. To somewhat remedy this situation, I made sure to back up the database every time
any commands modifying it were run.

### HTML/CSS
I extensively used Bootstrap, initially using their online version, but now using a local download. This was initially done
because I wanted to modify SASS variables, but later decided not to due to it being complex and the benefits of this being
very limited. 

### Javascript
I decided to use server-side validation for logging in and registering, because I wanted the user to know if the username was
taken or if their password is correct. I used the flash() function of flask for this purpose, with a js script that captures
these and puts them in an error array, which is then processed by the correct function. In hindsight, I believe using an error
API with await and fetch on the client side would have been much more scalable.

### Conclusion
Overall I am mostly happy with what I've made, however there are still potential issues/features that I'd like to fix/add, with
this in mind, I will be occasionally working on this as I use it on <https://github.com/Agamer102/Gametrack>.