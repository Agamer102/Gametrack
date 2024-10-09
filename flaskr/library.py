from flask import ( # type: ignore
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort # type: ignore

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('library', __name__)


@bp.route('/')
@login_required
def library():
    print(g.user['username']if g.user else None)
    db = get_db()

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
        args = request.form['game_id']
        print(args)
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

    if len(query) < 4:
        return redirect(url_for('library.library'))

    query_s = f'{query}%'
    query_e = f'%{query}'
    query_f = f'%{query}%'

    db = get_db()

    results = db.execute (
        'SELECT *,'
        ' (CASE'
        '   WHEN steamlibrary.name LIKE ? AND (vndblibrary.title_rm LIKE ? OR vndblibrary.title_en LIKE ?) THEN 6'
        '   WHEN steamlibrary.name LIKE ? OR vndblibrary.title_rm LIKE ? OR vndblibrary.title_en LIKE ? THEN 5'
        '   WHEN steamlibrary.name LIKE ? AND (vndblibrary.title_rm LIKE ? OR vndblibrary.title_en LIKE ?) THEN 4'
        '   WHEN steamlibrary.name LIKE ? OR vndblibrary.title_rm LIKE ? OR vndblibrary.title_en LIKE ? THEN 3'
        '   WHEN steamlibrary.name LIKE ? AND (vndblibrary.title_rm LIKE ? OR vndblibrary.title_en LIKE ?) THEN 2'
        '   WHEN steamlibrary.name LIKE ? OR vndblibrary.title_rm LIKE ? OR vndblibrary.title_en LIKE ? THEN 3'
        '   ELSE 0'
        '  END) AS relevance'
        ' FROM gamelibrary'
        '  LEFT JOIN steamlibrary ON gamelibrary.steam_appid = steamlibrary.id'
        '  LEFT JOIN vndblibrary ON gamelibrary.vndbid = vndblibrary.id'
        '  WHERE steamlibrary.name LIKE ?'
        '   OR vndblibrary.title_rm LIKE ?'
        '   OR vndblibrary.title_en LIKE ?'
        ' ORDER BY relevance DESC',
        (query, query, query, query, query, query,
         query_s, query_s, query_s, query_s, query_s, query_s,
         query_e, query_e, query_e, query_e, query_e, query_e,
         query_f, query_f, query_f)
    ).fetchall()

    results = list(map(dict, results))
    # print(results)

    return render_template('library/update.html', results=results)