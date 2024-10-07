DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS library;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  steam_id INTEGER
);

CREATE TABLE library (
  user_id INTEGER NOT NULL,
  game_id INTEGER NOT NULL,
  removed INTEGER NOT NULL DEFAULT 0,
  rating REAL,
  time INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (game_id) REFERENCES gamelibrary (id),
  UNIQUE (user_id, game_id)
);