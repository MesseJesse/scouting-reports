import json
import requests
import sys

player_id = sys.argv[1]
url = f"https://www.fotmob.com/api/data/playerData?id={player_id}"

response = requests.get(url)
player = response.json()

def get_stat(stats, stat_name):
    for stat in stats:
        if stat["title"] == stat_name:
            return stat["statValue"]
    return None

print("\n===== PLAYER =====")
print(f"Name: {player['name']}")
print(f"Club: {player['primaryTeam']['teamName']}")

for info in player["playerInformation"]:
    print(f"{info['title']}: {info['value']['fallback']}")

print("\n===== POSITION =====")
print(f"Primary: {player['positionDescription']['primaryPosition']['label']}")

print("\n===== CURRENT SEASON =====")
top_stats = player["firstSeasonStats"]["topStatCard"]["items"]

print(f"Goals: {get_stat(top_stats, 'Goals')}")
print(f"Assists: {get_stat(top_stats, 'Assists')}")
print(f"Rating: {get_stat(top_stats, 'Rating')}")
print(f"Matches: {get_stat(top_stats, 'Matches')}")
print(f"Started: {get_stat(top_stats, 'Started')}")
print(f"Minutes: {get_stat(top_stats, 'Minutes')}")

print("\n===== SEASON PERFORMANCE =====")
stats_section = player["firstSeasonStats"]["statsSection"]

for group in stats_section["items"]:
    print(f"\n{group['title']}")

    for stat in group["items"]:
        print(f"  {stat['title']}: {stat['statValue']}")

print("\n===== CAREER =====")

career = player["careerHistory"]["careerItems"]["senior"]["seasonEntries"]

for season in career:
    rating = season["rating"]["rating"]

    print(
        f"{season['seasonName']} | "
        f"{season['team']} | "
        f"{season['appearances']} apps | "
        f"{season['goals']} goals | "
        f"{season['assists']} assists | "
        f"Rating: {rating}"
    )