CREATE TABLE gamelibrary (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 steam_appid INTEGER,
 vndbid TEXT,
 UNIQUE (steam_appid, vndbid)
);

CREATE TABLE steamlibrary (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE vndblibrary (
 id TEXT PRIMARY KEY,
 title_en TEXT,
 title_rm TEXT,
 image TEXT,
 description TEXT,
 steam_appid INTEGER
);

INSERT INTO users (username, password)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');