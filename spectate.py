import argparse
from pathlib import Path

import lol_spectator


def spectate_by_summoner_name(api_key: str, platform_id, summoner_name: str, install_path: Path):
    try:
        summoner_id = lol_spectator.get_summoner_id(api_key, platform_id, summoner_name)
    except lol_spectator.SummonerDoesNotExist as error:
        print(error)
        return

    try:
        spectate_info = lol_spectator.get_spectate_info(api_key, platform_id, summoner_id)
    except lol_spectator.NotInGameError:
        print(f'{summoner_name} is not in game')
        return
    lol_spectator.spectate(spectate_info, install_path)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('install_path', type=Path, help='Path of your LoL install. For example, "C:/Games/League of Legends".')
    parser.add_argument('api_key', help='Developer API key from https://developer.riotgames.com/')
    parser.add_argument('platform_id', choices=lol_spectator.PLATFORM_IDS, help='Platform ID')
    parser.add_argument('summoner_name', help='Summoner name')
    args = parser.parse_args()

    spectate_by_summoner_name(args.api_key, args.platform_id, args.summoner_name, args.install_path)
    

if __name__ == '__main__':
    _main()
