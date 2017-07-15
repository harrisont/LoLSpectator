import subprocess
from collections import namedtuple
from pathlib import Path

import requests

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

PLATFORM_IDS = _SPECTATOR_HOST_BY_PLATFORM.keys()


def _get_api_host(platform_id: str):
    return f'{platform_id}.api.riotgames.com'


class SummonerDoesNotExist(Exception):
    pass


def get_summoner_id(api_key: str, platform_id: str, summoner_name: str) -> int:
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


SpectateGameInfo = namedtuple('SpectateGameInfo', ['platform_id', 'game_id', 'encryption_key'])


def get_spectate_info(api_key: str, platform_id: str, summoner_id: int) -> SpectateGameInfo:
    """
    Raises NotInGameError if the player is not currently in game.
    """
    # https://developer.riotgames.com/api-methods/#spectator-v3/GET_getCurrentGameInfoBySummoner
    result = requests.get(f'https://{_get_api_host(platform_id)}/lol/spectator/v3/active-games/by-summoner/{summoner_id}', params={'api_key': api_key})
    if result.status_code == 404:
        raise NotInGameError(f'Summoner with ID {summoner_id} on platform {platform_id} is not in game')
    result.raise_for_status()
    data = result.json()
    return SpectateGameInfo(platform_id=platform_id,
                            game_id=data['gameId'],
                            encryption_key=data['observers']['encryptionKey'])


def _get_lol_exe_dir(install_path: Path) -> Path:
    game_releases_dir = install_path / 'RADS/solutions/lol_game_client_sln/releases'
    release_dir = next(iter(game_releases_dir.iterdir()))
    return release_dir / 'deploy'


def spectate(spectate_info: SpectateGameInfo, install_path: Path) -> None:
    lol_exe_dir = _get_lol_exe_dir(install_path)
    spectator_host = _SPECTATOR_HOST_BY_PLATFORM[spectate_info.platform_id]
    command_line_args = [
        str(lol_exe_dir / 'League of Legends.exe'),
        '8394',  # Deprecated Maestro parameter
        'DefinitelyNotLeagueClient.exe',  # Deprecated Maestro Parameter
        '/this/path/is/bogus/but/the/game/doesnt/care',
        f'spectator {spectator_host} {spectate_info.encryption_key} {spectate_info.game_id} {spectate_info.platform_id}',
        '-UseRads',
    ]
    subprocess.run(command_line_args, cwd=str(lol_exe_dir), check=True)
