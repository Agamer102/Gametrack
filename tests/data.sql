INSERT INTO users (username, password)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO games (name, steam_appid, vndbid)
VALUES
  ('Aokana - Four Rhythms Across the Blue', 1044620, 12849),
  ('Sabbat of the Witch',888790, 16044);

INSERT INTO library (user_id, game_id, rating, time)
VALUES
  (1, 1, NULL, 1440),
  (2, 1, 9.7, 3000);