import os
import sqlite3
import shutil

import click  # type: ignore
import requests # type: ignore
import tarfile
import zstandard as zstd # type: ignore
import pandas as pd # type: ignore
from rich.console import Console # type: ignore
from rich.progress import track, Progress, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, TimeElapsedColumn, TaskProgressColumn # type: ignore
from flask import current_app, g # type: ignore


console = Console()

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
    
    print('Applist of', len(applist))
    
    db.execute('DROP TABLE IF EXISTS steamlibrary')
    db.execute(
        'CREATE TABLE steamlibrary ('
        ' id INTEGER PRIMARY KEY,'
        ' name TEXT NOT NULL'
        ')'
    )
    db.execute('BEGIN TRANSACTION')
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        ) as progress:
        task = progress.add_task("Loading Steam library...", total=len(applist))
        for app in applist:
            try:
                db.execute(
                    'INSERT INTO steamlibrary (id, name) VALUES (?, ?)',
                    (app['appid'], app['name'])
                )
            except db.IntegrityError:
                pass
            progress.update(task, advance=1)
    
    db.execute('COMMIT')
    db.execute('CREATE INDEX steamlibrary_name_index ON steamlibrary (name)')
    db.commit()


def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kilobyte

    with open(filename, 'wb') as file:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("Downloading...", total=total_size)
                for data in response.iter_content(block_size):
                    file.write(data)
                    progress.update(task, advance=len(data))


def load_vndb_library(nodl_vndb):
    FILES = [
    'vn', 'vn_titles', 'releases', 'releases_vn',
    ]

    TABLES = ['vndb_' + name for name in FILES]

    HEADERS = [
        'id', 'image', 'description', 'olang', 'lang', 'title',
        'official', 'latin', 'l_steam', 'vid', 'rtype'
    ]

    if nodl_vndb != True:
        download_file('https://dl.vndb.org/dump/vndb-db-latest.tar.zst', current_app.instance_path + '/vndb-db-latest.tar.zst')

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn()
        ) as progress:

        decompress_task = progress.add_task("Decompressing...", total=1)
        with open(current_app.instance_path + '/vndb-db-latest.tar.zst', 'rb') as file:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(file) as reader:
                with tarfile.open(fileobj=reader, mode='r:') as tar:
                    tar.extractall(path=current_app.instance_path + '/extracted_files')
        progress.update(decompress_task, advance=1)

        db = get_db()
        insert_task = progress.add_task("Inserting data...", total=len(FILES))
        for i, file in enumerate([current_app.instance_path + '/extracted_files/db/' + file for file in FILES]):
            headers = pd.read_csv(file + '.header', delimiter='\t').columns.tolist()
            dtype_dict = {col: 'str' for col in headers}
            df = pd.read_csv(file, delimiter='\t', names=headers, dtype=dtype_dict)
            df = df.filter(items=[header for header in headers if header in HEADERS])

            table_name = 'vndb_' + FILES[i]

            # Warning be absolutely sure this is server only
            db.execute(f'DROP TABLE IF EXISTS {table_name}')
            db.commit()

            df.to_sql(table_name, db, if_exists='append', index=False)
            progress.update(insert_task, advance=1)


        steam_vns = db.execute (
            f'SELECT * FROM {TABLES[2]} JOIN {TABLES[3]} ON {TABLES[3]}.id = {TABLES[2]}.id'
            ' WHERE l_steam != 0'
        ).fetchall()
        steam_vns = list(map(dict, steam_vns))

        titles = db.execute (
            f'SELECT * FROM {TABLES[1]}'
            f' WHERE lang = "ja" OR lang = "en"'
        ).fetchall()
        titles = list(map(dict, titles))

        vns = db.execute (
            f'SELECT * FROM {TABLES[0]}'
        ).fetchall()
        vns = list(map(dict, vns))

        # Create table
        db.execute('DROP TABLE IF EXISTS vndblibrary')
        db.execute(
            'CREATE TABLE vndblibrary ('
            ' id TEXT PRIMARY KEY,'
            ' title_en TEXT,'
            ' title_rm TEXT,'
            ' image TEXT,'
            ' description TEXT,'
            ' steam_appid INTEGER'
            ')'
        )

        # FINALLY insert this data
        final_task = progress.add_task("Finalising data...", total=len(vns))
        db.execute('BEGIN TRANSACTION')
        for vn in vns:
            progress.update(final_task, advance=1)

            id = vn['id']
            titles_vn = [title for title in titles if title['id'] == id and title['official'] == 't']
            title_en = None
            title_rm = None
            steam_appid = None
            for title_vn in titles_vn:
                if title_vn['lang'] == 'en':
                    title_en = title_vn['title']
                if title_vn['lang'] == vn['olang']:
                    title_rm = title_vn['latin'] if title_vn['latin'] != "\\N" else title_vn['title']
            for steam_vn in steam_vns:
                if steam_vn['vid'] == id:
                    steam_appid = steam_vn['l_steam']
                    break

            # print(id, title_en, title_rm, steam_appid)
            try:
                db.execute (
                    'INSERT INTO vndblibrary (id, title_en, title_rm, image, description, steam_appid)'
                    ' VALUES (?, ?, ?, ?, ?, ?)',
                    (id, title_en, title_rm, f'https://t.vndb.org/{vn["image"][:2]}/{vn["image"][-2:]}/{vn["image"][2:]}.jpg', vn['description'], steam_appid)
                )
            except db.IntegrityError:
                pass
        
        db.execute('COMMIT')

        # Clean up temporary tables
        for table in TABLES:
            db.execute(f'DROP TABLE {table}')

        #Delete temporary files
        shutil.rmtree(current_app.instance_path + '/extracted_files')

        
def load_gamelibrary():
    db = get_db()
    # Create table
    db.execute('DROP TABLE IF EXISTS gamelibrary')
    db.execute(
        'CREATE TABLE gamelibrary ('
        ' id INTEGER PRIMARY KEY AUTOINCREMENT,'
        ' steam_appid INTEGER,'
        ' vndbid TEXT,'
        ' UNIQUE (steam_appid, vndbid)'
        ' )'
    )

    db.execute(
        'INSERT INTO gamelibrary (steam_appid, vndbid)'
        ' SELECT steamlibrary.id, vndblibrary.id FROM'
        '  steamlibrary LEFT JOIN vndblibrary ON steamlibrary.id = vndblibrary.steam_appid'
        ' UNION'
        ' SELECT steamlibrary.id, vndblibrary.id FROM'
        '  vndblibrary LEFT JOIN steamlibrary ON steamlibrary.id = vndblibrary.steam_appid'
    )
    db.commit()



@click.command('init-db')
@click.option('--keep-users',is_flag=True, help='Keep the existing users and their data.')
@click.option('--keep-games', is_flag=True, help='Keep the existing game database.')
@click.option('--keep-steam', is_flag=True, help='Keep the existing Steam database')
@click.option('--keep-vndb', is_flag=True, help='Keep the existing VNDB database.')
@click.option('--nodl-vndb', is_flag=True, help='Do not re-download VNDB database.')
def init_db_command(keep_users, keep_games, keep_steam, keep_vndb, nodl_vndb):
    """Clear the existing data and create new tables."""

    if keep_users != True:
        console.print('[bold blue]Initializing the database[/bold blue]')
        init_db()

    if keep_games != True:
        if keep_steam != True:
            load_steamlibrary()

        if keep_vndb != True:
            console.print('[bold blue]Loading VNDB library[/bold blue]')
            load_vndb_library(nodl_vndb)

        load_gamelibrary()

    console.print('[bold green]Database has been initialized[/bold green]')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
