import requests
import sys
import json

player_id = sys.argv[1]

url = f"https://www.fotmob.com/api/data/playerData?id={player_id}"

response = requests.get(url)
response.raise_for_status()

player = response.json()

print(f"Player: {player['name']}")

print("\n===== STAT SEASONS =====")

print(json.dumps(player["statSeasons"], indent=2))