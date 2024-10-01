import os
import sqlite3
import sys

import click # type: ignore
import csv
import requests # type: ignore
import tarfile
import zstandard as zstd # type: ignore
import io
import pandas as pd # type: ignore
import time
import threading
from tqdm import tqdm # type: ignore
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
    
def loading_screen():
    global stop_loading
    while not stop_loading:
        for _ in track(range(50), description="Loading..."):
            time.sleep(0.1)  # Simulate work being done

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
    end_l_time = time.time()
    l_time = end_l_time - start_l_time 
    
    start_i_time = time.time()
    db.execute('CREATE INDEX steamlibrary_name_index ON steamlibrary (name)')
    db.commit()
    end_i_time = time.time()
    i_time = end_i_time - start_i_time 

    return f'Initialized Steam library.\nLoad time: {l_time:.3f} S\nIndex time: {i_time:.3f} S'


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


def load_vndb_library(keep_vndb):
    FILES = [
    'vn', 'vn_titles', 'releases', 'releases_vn',
    ]

    if keep_vndb != True:
        download_file('https://dl.vndb.org/dump/vndb-db-latest.tar.zst', current_app.instance_path + '/vndb-db-latest.tar.zst')

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn()
        ) as progress:

        if keep_vndb != True:
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
            df.to_sql('vndb_' + FILES[i], db, if_exists='append', index=False)
            progress.update(insert_task, advance=1)
        

@click.command('init-db')
@click.option('--keep-vndb', is_flag=True, help='Keep exsiting vndb databse.')
def init_db_command(keep_vndb):
    """Clear the existing data and create new tables."""

    console.print('[bold blue]Initializing the database[/bold blue]')
    init_db()

    load_steamlibrary()
    console.print('Loading VNDB library...')

    load_vndb_library(keep_vndb)


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
