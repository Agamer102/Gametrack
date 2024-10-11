# Gametrack
#### Video Demo:  
## Overview
//todo
## Requirements

All the requirements are included in the pyproject.toml file

## Installation

* Create a virtual environment by running
 * python3 -m venv .venv
 * . .venv/bin/activate (on Mac/Linux)
 * .venv\Scripts\activate (on Windows)
* Run: pip install build
* Run: python -m build --wheel
* Run: pip install name of the file here
* Create a config.py file in the instance directory (.venv/var/gametrack-instance)
* Generate a secure key by running python -c 'import secrets; print(secrets.token_hex())'
* Set SECRET_KEY = 'value you generated'
* Get a Steam API key from https://steamcommunity.com/dev/apikey
* Set STEAM_API_KEY = 'your steam api key'


## Usage

/ToDo

## Contributing

I most likely will not be accepting any contributions , as I am new to github and python. However feel free to use any part or whole of this program for your own usecases !

CS50X final project of Adithya Dissanayake