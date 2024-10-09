import functools

from flask import ( # type: ignore
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash # type: ignore

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request
def load_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirmPassword']
        db = get_db()
        errors = []

        if not username:
            errors.append(0)
        if not password:
            errors.append(1)
        if not confirm:
            errors.append(2)
        if confirm != password:
            errors.append(3)

        if not errors:
            try:
                db.execute(
                    'INSERT INTO users (username, password) VALUES (?, ?)',
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                errors.append(4)
            else:
                session.clear()
                return redirect(url_for('auth.login'))
        
        for error in errors:
            flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        errors = []

        if not username:
            errors.append(0)
        if not password:
            errors.append(1)

        if not errors:
            user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
            ).fetchone()

            if user is None:
                errors.append(5)
            elif not check_password_hash(user['password'], password):
                errors.append(6)

            if not errors:
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('library.library'))
        
        for error in errors:
            flash(error)
    
    return render_template('auth/login.html')


@bp.route('logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view) # type: ignore
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs) # type: ignore
    
    return wrapped_view