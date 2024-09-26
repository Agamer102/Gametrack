import os

import json
import requests # type: ignore
from flask import ( # type: ignore
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort # type: ignore

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('steam', __name__, url_prefix='/steam')

@bp.before_app_request
def load_api_key():
    g.steam_api_key = os.getenv('STEAM_API_KEY')
    if g.steam_api_key == 'invalid':
        abort(500)


@bp.route('/load', methods=('GET', 'POST')) 
@login_required
def load():
    if request.method == 'POST':
        print('POST request received')
        steamid = request.form['id']
        print(f'Steam ID: {steamid}')
        response = requests.get(
            f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={g.steam_api_key}&steamid={steamid}&include_appinfo=true&format=json'
        ).json()['response']
        print('RESPONSE GOT')
        if not response:
            print('NO RESPONSE')
        else:
            print(response['games'])
            for game in response['games']:
                print(game)
                db = get_db()
                try:
                    db.execute(
                        'INSERT INTO games (name, steam_appid) VALUES (?, ?)',
                        (game['name'], game['appid'])
                    )
                except db.IntegrityError:
                    pass
                game_id = db.execute(
                    'SELECT id FROM games WHERE name = ? ORDER BY id',
                    (game['name'],)
                ).fetchone()['id']
                try:
                    db.execute(
                        'INSERT INTO library (user_id, game_id, time)'
                        ' VALUES (?, ?, ?)',
                        (g.user['id'], game_id, game['playtime_forever'] + game['playtime_disconnected'])
                    )
                except db.IntegrityError:
                    db.execute(
                        'UPDATE library SET time = ?'
                        ' WHERE user_id = ? AND game_id = ?',
                        (game['playtime_forever'] + game['playtime_disconnected'], g.user['id'], game_id)
                    )

                db.commit()

    return redirect(url_for('library.library'))


def request_game(appid):
    response = requests.get(
        url="http://store.steampowered.com/api/appdetails/", params={"appids": appid}
    ).json()
    try:
        if response:
            return {"steam_appid": appid, "name": response[appid]["data"]["name"]}
        else:
            return 'invalid'
    except KeyError:
        return 'invalid'
    
