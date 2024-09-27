DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS library;
DROP TABLE IF EXISTS steamlibrary;
DROP TABLE IF EXISTS vndblibrary;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  steam_id INTEGER
);

CREATE TABLE games (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  steam_appid INTEGER UNIQUE,
  vndbid INTEGER
);

CREATE TABLE steamlibrary (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  vndbid TEXT,
  FOREIGN KEY (vndbid) REFERENCES vndblibrary(id)
);

CREATE TABLE vndblibrary (
  id TEXT PRIMARY KEY,
  name_en TEXT,
  name_romaji TEXT,
  steam_appid INTEGER,
  image TEXT,
  FOREIGN KEY (steam_appid) REFERENCES steamlibrary(id)
);

CREATE TABLE library (
  user_id INTEGER NOT NULL,
  game_id INTEGER NOT NULL,
  removed INTEGER NOT NULL DEFAULT 0,
  rating REAL,
  time INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (game_id) REFERENCES games(id),
  UNIQUE (user_id, game_id)
);