from flask import ( # type: ignore
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort # type: ignore

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.steam import request_game

bp = Blueprint('library', __name__)


@bp.route('/',methods=('GET', 'POST'))
@login_required
def library():
    db = get_db()
    library = db.execute(
        'SELECT game_id, name, removed, steam_appid, vndbid, rating, time '
        ' FROM library '
        '  JOIN games ON library.game_id = games.id '
        ' WHERE library.user_id = ?',
        (g.user['id'],)
    ).fetchall()
    library = list(map(dict, library))

    if request.method == 'POST':
        input_type = request.form['select_val']
        valid_types = ['name', 'steam_appid', 'vndbid']
        id = request.form.getlist('id')
        time = request.form['time']
        rating = request.form['rating']
        error = None
        
        for c in id:
            if c == '':
                continue
            else:
                id = c
                break
        else:
            error = 'Invalid name or id.'
                

        if input_type not in valid_types:
            error = 'Invalid selection.'    
        elif not time.isnumeric():
            error = 'Time played is missing or invalid.'
        elif rating and not rating.isnumeric():
            error = 'Invalid rating.'

        if error is not None:
            flash(error)
        else:
            if input_type == 'name':
                db.execute(
                    'INSERT INTO games (name) VALUES (?)',
                    (id,)
                )
                game_id = db.execute(
                    'SELECT id FROM games WHERE name = ? ORDER BY id',
                    (id,)
                ).fetchone()['id']
                db.execute(
                    'INSERT INTO library (user_id, game_id, rating, time)'
                    ' VALUES (?, ?, ?, ?)',
                    (g.user['id'], game_id, rating, time)
                )
                db.commit()
            elif input_type == 'steam_appid':
                game = request_game(str(id))
                if game == 'invalid':
                    print('invalid id')
                    flash('Invalid Steam AppID.')
                else:
                    db.execute(
                        'INSERT INTO games (name, steam_appid)'
                        ' VALUES (?, ?)',
                        (game['name'], game['steam_appid'])
                    )
                    game_id = db.execute(
                        'SELECT id FROM games WHERE steam_appid = ? ORDER BY id',
                        (id,)
                    ).fetchone()['id']
                    db.execute(
                    'INSERT INTO library (user_id, game_id, rating, time)'
                    ' VALUES (?, ?, ?, ?)',
                    (g.user['id'], game_id, rating, time)
                    )
                    db.commit()
            else:
                flash('Unsupported selection.')

    
    return render_template('library/library.html', library=library)


@bp.route('/update', methods=('GET', 'POST'))
@login_required
def update():
    if request.method == 'POST':
        s=1
    
    game_id = request.args.get('game_id')
    db = get_db()
    game = db.execute(
        'SELECT game_id, name, removed, steam_appid, vndbid, rating, time '
        ' FROM library '
        '  JOIN games ON library.game_id = games.id '
        ' WHERE library.user_id = ? AND game_id = ?',
        (g.user['id'], game_id)
    ).fetchone()

    if game == None:
        return redirect(url_for('library.library'))

    game = dict(game)
    print(game)
    return render_template('library/update.html', game=game)