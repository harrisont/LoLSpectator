# LoLSpectator
Spectate LoL games

## Setup
1. `pip install pip-tools`
2. `pip-sync`

## Usage
1. Get developer API key from https://developer.riotgames.com/.
2. `python spectate.py API_KEY PLATFORM_ID SUMMONER_NAME`

## Development

### Update Requiremnets
1. Change the requirements in `requirements.in`.
2. `pip-compile`
3. `pip-sync`
