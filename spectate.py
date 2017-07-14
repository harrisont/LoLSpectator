from typing import Dict

import requests

# From https://developer.riotgames.com/
_PLATFORM_ID = 'NA1'
_SUMMONER_NAME = 'Rioting'
_API_KEY = 'RGAPI-70214411-99f0-4b0f-a4d5-2afa63f09a6a'


class SummonerDoesNotExist(Exception):
    pass


def _get_summoner_id() -> int:
    result = requests.get(f'https://{_PLATFORM_ID}.api.riotgames.com/lol/summoner/v3/summoners/by-name/{_SUMMONER_NAME}', params={'api_key': _API_KEY})
    if result.status_code == 404:
        raise SummonerDoesNotExist(f'No summoner with name {_SUMMONER_NAME} found on platform {_PLATFORM_ID}')
    result.raise_for_status()
    data = result.json()
    return data['id']


class NotInGameError(Exception):
    pass


def _get_spectator_game_info(summoner_id: int) -> Dict:
    result = requests.get(f'https://{_PLATFORM_ID}.api.riotgames.com/observer-mode/rest/consumer/getSpectatorGameInfo/{_PLATFORM_ID}/{summoner_id}', params={'api_key': _API_KEY})
    if result.status_code == 404:
        raise NotInGameError(f'No summoner with ID {summoner_id} found on platform {_PLATFORM_ID}')
    result.raise_for_status()
    data = result.json()
    return data


def _spectate():
    summoner_id = _get_summoner_id()
    try:
        data = _get_spectator_game_info(summoner_id)
        print(data)
    except NotInGameError:
        print('Not in game')


def _main():
    _spectate()
    

if __name__ == '__main__':
    _main()
