import argparse
from collections import namedtuple
import os
import subprocess

import requests


_INSTALL_PATH = 'C:/Games/League of Legends'

_SPECTATOR_HOST_BY_PLATFORM = {
    'NA1': 'spectator.na.lol.riotgames.com:80',
    'EUW1': 'spectator.euw1.lol.riotgames.com:80',
    'EUN1': 'spectator.eu.lol.riotgames.com:8088',
    'JP1': 'spectator.jp1.lol.riotgames.com:80',
    'KR': 'spectator.kr.lol.riotgames.com:80',
    'OC1': 'spectator.oc1.lol.riotgames.com:80',
    'BR1': 'spectator.br.lol.riotgames.com:80',
    'LA1': 'spectator.la1.lol.riotgames.com:80',
    'LA2': 'spectator.la2.lol.riotgames.com:80',
    'RU': 'spectator.ru.lol.riotgames.com:80',
    'TR1': 'spectator.tr.lol.riotgames.com:80',
    'PBE1': 'spectator.pbe1.lol.riotgames.com:8088',
}


def _get_api_host(platform_id: str):
    return f'{platform_id}.api.riotgames.com'


class SummonerDoesNotExist(Exception):
    pass


def _get_summoner_id(api_key: str, platform_id: str, summoner_name: str) -> int:
    """
    Raises SummonerDoesNotExist if there is no summer with that name.
    """
    # https://developer.riotgames.com/api-methods/#summoner-v3/GET_getBySummonerName
    result = requests.get(f'https://{_get_api_host(platform_id)}/lol/summoner/v3/summoners/by-name/{summoner_name}', params={'api_key': api_key})
    if result.status_code == 404:
        raise SummonerDoesNotExist(f'No summoner with name "{summoner_name}" found on platform {platform_id}')
    result.raise_for_status()
    data = result.json()
    return data['id']


class NotInGameError(Exception):
    pass


_SpectateGameInfo = namedtuple('SpectateGameInfo', ['platform_id', 'game_id', 'encryption_key'])


def _get_spectate_info(api_key: str, platform_id: str, summoner_id: int) -> _SpectateGameInfo:
    """
    Raises NotInGameError if the player is not currently in game.
    """
    # https://developer.riotgames.com/api-methods/#spectator-v3/GET_getCurrentGameInfoBySummoner
    result = requests.get(f'https://{_get_api_host(platform_id)}/lol/spectator/v3/active-games/by-summoner/{summoner_id}', params={'api_key': api_key})
    if result.status_code == 404:
        raise NotInGameError(f'Summoner with ID {summoner_id} on platform {platform_id} is not in game')
    result.raise_for_status()
    data = result.json()
    return _SpectateGameInfo(platform_id=platform_id,
                             game_id=data['gameId'],
                             encryption_key=data['observers']['encryptionKey'])


def _spectate(spectate_info: _SpectateGameInfo) -> None:
    # TODO: Get from discovering release path
    lol_exe_dir = os.path.join(_INSTALL_PATH, 'RADS/solutions/lol_game_client_sln/releases/0.0.1.181/deploy')
    spectator_host = _SPECTATOR_HOST_BY_PLATFORM[spectate_info.platform_id]
    command_line_args = [
        os.path.join(lol_exe_dir, 'League of Legends.exe'),
        '8394',  # Deprecated Maestro parameter
        'DefinitelyNotLeagueClient.exe',  # Deprecated Maestro Parameter
        '/this/path/is/bogus/but/the/game/doesnt/care',
        f'spectator {spectator_host} {spectate_info.encryption_key} {spectate_info.game_id} {spectate_info.platform_id}',
        '-UseRads',
    ]
    subprocess.run(command_line_args, cwd=lol_exe_dir, check=True)


def _spectate_by_summoner(api_key: str, platform_id, summoner_name):
    try:
        summoner_id = _get_summoner_id(api_key, platform_id, summoner_name)
    except SummonerDoesNotExist as error:
        print(error)
        return

    try:
        spectate_info = _get_spectate_info(api_key, platform_id, summoner_id)
    except NotInGameError:
        print(f'{summoner_name} is not in game')
        return
    _spectate(spectate_info)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('api_key', help='Developer API key from https://developer.riotgames.com/')
    parser.add_argument('platform_id', choices=_SPECTATOR_HOST_BY_PLATFORM.keys(), help='Platform ID')
    parser.add_argument('summoner_name', help='Summoner name')
    args = parser.parse_args()

    _spectate_by_summoner(args.api_key, args.platform_id, args.summoner_name)
    

if __name__ == '__main__':
    _main()
