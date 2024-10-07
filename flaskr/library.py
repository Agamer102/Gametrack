from flask import ( # type: ignore
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort # type: ignore

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.steam import request_game
from flaskr.vndb import request_game_vndb_steamid

bp = Blueprint('library', __name__)


@bp.route('/',methods=('GET', 'POST'))
@login_required
def library():
    db = get_db()
   
    if request.method == 'POST':
        """
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
                """

    #first get the users games
    user_library = db.execute(
        'SELECT * FROM library'
        ' JOIN gamelibrary ON library.game_id = gamelibrary.id'
        ' WHERE library.user_id = ?',
        (g.user['id'],)
    ).fetchall()
    user_library = list(map(dict, user_library))

    for entry in user_library:
        if entry['vndbid']:
            entry['name'] = db.execute (
                'SELECT title_rm FROM vndblibrary WHERE id = ?',
                (entry['vndbid'],)
            ).fetchone()['title_rm']
            image = db.execute (
                'SELECT image FROM vndblibrary WHERE id = ?',
                (entry['vndbid'],)
            ).fetchone()['image']
            entry['image'] = f'https://t.vndb.org/{image[:2]}/{image[-2:]}/{image[2:]}.jpg'
        if entry['steam_appid']:
            entry['name'] = db.execute (
                'SELECT name FROM steamlibrary WHERE id = ?',
                (entry['steam_appid'],)
            ).fetchone()['name']
        # print(entry)

    return render_template('library/library.html', user_library=user_library)


@bp.route('/update', methods=('GET', 'POST'))
@login_required
def update():
    if request.method == 'POST':
        s=1
    return redirect(url_for('library.library'))


@bp.route('/delete', methods=('GET', 'POST'))
@login_required
def delete():
    if request.method == 'POST':
        user_id = g.user['id']
        game_id = request.form['game_id']

        db = get_db()
        db.execute (
            'UPDATE library SET removed = 1 WHERE'
            ' user_id = ? AND game_id = ?',
            (user_id, game_id)
        )
        db.commit()

    return redirect(url_for('library.library'))


@bp.route('/search')
def search():
    query = request.args['q']

    if len(query) > 4:
        query = f'%{request.args["q"]}%'

    db = get_db()

    # check steam database

    steam_r = db.execute (
        'SELECT * FROM steamlibrary WHERE name LIKE ?',
        (query,)
    ).fetchall()
    steam_r = list(map(dict, steam_r))
    print(steam_r)

    vndb_r = db.execute (
        'SELECT * FROM vndblibrary WHERE'
        ' title_en LIKE ? OR title_rm LIKE ?',
        (query, query)
    ).fetchall()
    vndb_r = list(map(dict, vndb_r))
    print(vndb_r)

    return render_template('library/update.html', steam_r=steam_r, vndb_r=vndb_r)