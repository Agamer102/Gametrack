import os

import json
import requests # type: ignore
from flask import ( # type: ignore
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort # type: ignore

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('vndb', __name__, url_prefix='/vndb')

@bp.before_app_request
def load_api_key():
    s=2


@bp.route('/load', methods=('GET', 'POST'))
@login_required
def load():
    """
    if request.method == 'POST':
        username = request.form['username']
        user_id = requests.get(
            f'https://api.vndb.org/kana/user?q={username}'
        ).json()[username]['id']
        print(user_id)
        data = {
            'user': user_id,
            'fields': 'id, vn.title, vn.image.url, vn.editions.eid'
        }
        response = requests.post(
            url='https://api.vndb.org/kana/ulist', json=data
        )
        print(response)
        response=response.json()
        print(response)
    """
    return redirect(url_for('library.library'))

@bp.route('/link', methods=('GET', 'POST'))
@login_required
def link():
    db = get_db()
    steam_appids = db.execute(
        'SELECT steam'
    )

def request_game_vndb(vndbid):
    s=3

def request_game_vndb_steamid(steamid):
    data = {
        'filters': ['extlink','=',['steam',702050]],
        'fields': 'id, title, vns.title'
    }
    response = requests.post(
        url='https://api.vndb.org/kana/release', json=data
    )
    if response.status_code == 200:
        response = response.json()
        return response['results'][0]['vns'][0]['id']
    else:
        return None
