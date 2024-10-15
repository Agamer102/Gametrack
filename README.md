# Gametrack
#### Video Demo:  removed
## Overview
This is a simple flask web app for a server to keep track of user's games.
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

path = '/home/Agamer102/.virtualenvs/my-virtualenv/lib/python3.10/site-packages/gametrack'
if path not in sys.path:
    sys.path.append(path)

from gametrack import create_app # noqa

application = create_app()

## Contributing

I'll keep working on this on my free time.
If you want to see the site visit <https://agamer102.pythonanywhere.com/>

CS50X final project of Adithya Dissanayake