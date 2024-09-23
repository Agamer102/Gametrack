import pytest # type: ignore

from flaskr import steam


def test_request_game():
    assert steam.request_game('1044620') == {'steam_appid': '1044620', 'name': 'Aokana - Four Rhythms Across the Blue'}
    assert steam.request_game('888790') == {'steam_appid': '888790', 'name': 'Sabbat of the Witch'}
    assert steam.request_game('743284') == 'invalid'