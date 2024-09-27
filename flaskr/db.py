import os
import sqlite3

import click # type: ignore
import csv
import requests # type: ignore
import tarfile
import time
from flask import current_app, g # type: ignore


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    

def load_steamlibrary():
    db = get_db()

    try:
        response = requests.get('http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json').json()
    except ValueError:
        return 'Failed to get steam library.'
    
    try:
        applist = response['applist']['apps']
    except KeyError or TypeError:
        return 'Response was unable to be decoded.'
     
    start_l_time = time.time()
    db.execute('BEGIN TRANSACTION')
    for app in applist:
        try:
            db.execute(
                'INSERT INTO steamlibrary (id, name) VALUES (?, ?)',
                (app['appid'], app['name'])
            )
        except db.IntegrityError:
            pass
    
    db.execute('COMMIT')
    end_l_time = time.time()
    l_time = end_l_time - start_l_time 
    
    start_i_time = time.time()
    db.execute('CREATE INDEX steamlibrary_name_index ON steamlibrary (name)')
    db.commit()
    end_i_time = time.time()
    i_time = end_i_time - start_i_time 

    return f'Initialized Steam library.\nLoad time: {l_time:.3f} S\nIndex time: {i_time:.3f} S'


def load_vndb_library():
    db = get_db()

    """
    here we must get vn, releases and releases_vn and all their headers to properly process
    currently this is being done manually but must be set to auto get from the link
    https://dl.vndb.org/dump/vndb-db-latest.tar.zst and must be unzipped and processed
    """
    vn_titles_header = []
    with open(current_app.instance_path + '/vndb/vn_titles.header', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f , delimiter='\t')
        vn_header = next(reader)

    with open(current_app.instance_path + '/vndb/vn_titles', mode='r', encoding='utf-8') as f:
        dict_reader = csv.DictReader(f, fieldnames=vn_titles_header, delimiter='\t')
        for row in dict_reader:
            s=1
            # do thing




@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
    click.echo('Loading Steam library...')
    click.echo(load_steamlibrary())
    load_vndb_library()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
