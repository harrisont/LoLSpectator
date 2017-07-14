import requests

# From https://developer.riotgames.com/
_API_KEY = 'RGAPI-70214411-99f0-4b0f-a4d5-2afa63f09a6a'


def _spectate():
    result = requests.get('https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/Rioting', params={'api_key': _API_KEY})
    result.raise_for_status()
    data = result.json()
    print(data)


def _main():
    _spectate()
    

if __name__ == '__main__':
    _main()
