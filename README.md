# GameList
#### Video Demo:  <https://youtu.be/UiZeXK7X6oI>
## Overview

Gamelist, a simple command-line Python script that can help you keep track of the games you've played and the time you've played it for.
It's very common that many people have different launchers and sites for different games that all individually keep track of your playtime, or not at all. 
This program offers a solution to this problem in the form of a simple command-line script, that can add, remove, or change the time played of any game.
It also supports importing your Steam library (requires free Steam API key) and adding games via steam appid. The program saves the data persistently as a .csv file that can be copied and elsewhere.

## Requirements

All the requirements are included in the pyproject.toml file

## Installation

* Create a virtual environment by running
 * python3 -m venv .venv
 * . .venv/bin/activate (on Mac/Linux)
 * .venv\Scripts\activate (on Windows)
* Run: pip install build
* Run: python -m build --wheel
* Run: pip install <name of the file here>
* Create a config.py file in the instance directory (.venv/var/gametrack-instance)
* Generate a secure key by running python -c 'import secrets; print(secrets.token_hex())'
* Set SECRET_KEY = 'value you generated'
* Get a Steam API key from https://steamcommunity.com/dev/apikey
* Set STEAM_API_KEY = 'your steam api key'


## Usage

/ToDo

## Contributing

I most likely will not be accepting any contributions , as I am new to github and python. However feel free to use any part or whole of this program for your own usecases !

CS50P final project of Adithya Dissanayake