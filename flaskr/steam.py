import requests # type: ignore

def request_game(appid):
    response = requests.get(
        url="http://store.steampowered.com/api/appdetails/", params={"appids": appid}
    ).json()
    try:
        if response:
            return {"steam_appid": appid, "name": response[appid]["data"]["name"]}
        else:
            return 'invalid'
    except KeyError:
        return 'invalid'
    
def get_libary(steamid):
    s=3