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
        # print('POST request received')
        steamid = request.form['id']
        # print(f'Steam ID: {steamid}')
        response = requests.get(
            f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={g.steam_api_key}&steamid={steamid}&include_appinfo=true&format=json'
        ).json()['response']
        # print('RESPONSE GOT')
        if not response:
            print('NO RESPONSE')
        else:
            # print(response['games'])
            for game in response['games']:
                # print(game)
                db = get_db()
                # print(game['appid'])
                game_id = db.execute (
                    'SELECT id FROM gamelibrary WHERE steam_appid = ?', (game['appid'],)
                ).fetchone()['id']
                # print(game_id)
                try:
                    db.execute(
                        'INSERT INTO library (user_id, game_id, steam_sync, time)'
                        ' VALUES (?, ?, ?, ?)',
                        (g.user['id'], game_id, 1, game['playtime_forever'] + game['playtime_disconnected'])
                    )
                except db.IntegrityError:
                    db.execute(
                        'UPDATE library SET time = ?'
                        ' WHERE user_id = ? AND game_id = ? AND steam_sync = 1',
                        (game['playtime_forever'] + game['playtime_disconnected'], g.user['id'], game_id)
                    )

                db.commit()

    return redirect(url_for('library.library'))
