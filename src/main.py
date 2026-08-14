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

def extract_player_info(player):
    information = player["playerInformation"]

    contract_end = information[5]["value"]["fallback"]

    if isinstance(contract_end, dict):
        contract_end = contract_end["utcTime"][:10]

    return {
        "name": player["name"],
        "club": player["primaryTeam"]["teamName"],
        "shirt": information[0]["value"]["fallback"],
        "age": information[1]["value"]["fallback"],
        "preferred_foot": information[2]["value"]["fallback"],
        "country": information[3]["value"]["fallback"],
        "market_value": information[4]["value"]["fallback"],
        "contract_end": contract_end,
    }

def extract_position(player):
    position = player["positionDescription"]

    return {
        "primary": position["primaryPosition"]["label"],
        "secondary": [
            pos["label"]
            for pos in position["nonPrimaryPositions"]
        ]
    }

def extract_current_season(player):
    stats = player["firstSeasonStats"]["topStatCard"]["items"]

    return {
        "goals": get_stat(stats, "Goals"),
        "assists": get_stat(stats, "Assists"),
        "rating": get_stat(stats, "Rating"),
        "matches": get_stat(stats, "Matches"),
        "started": get_stat(stats, "Started"),
        "minutes": get_stat(stats, "Minutes"),
    }

def extract_season_performance(player):
    stats_section = player["firstSeasonStats"]["statsSection"]

    performance = {}

    for group in stats_section["items"]:
        group_name = group["title"].lower()

        performance[group_name] = {}

        for stat in group["items"]:
            performance[group_name][stat["title"]] = stat["statValue"]

    return performance

def extract_career(player):
    seasons = player["careerHistory"]["careerItems"]["senior"]["seasonEntries"]

    career = []

    for season in seasons:
        career.append({
            "season": season["seasonName"],
            "team": season["team"],
            "appearances": season["appearances"],
            "goals": season["goals"],
            "assists": season["assists"],
            "rating": season["rating"].get("rating") if season.get("rating") else None,
        })

    return career

def extract_recent_matches(player):
    matches = player["recentMatches"]

    recent_matches = []

    for match in matches:
        recent_matches.append({
            "date": match["matchDate"]["utcTime"],
            "team": match["teamName"],
            "opponent": match["opponentTeamName"],
            "home": match["isHomeTeam"],
            "score": f"{match['homeScore']}-{match['awayScore']}",
            "minutes": match["minutesPlayed"],
            "goals": match["goals"],
            "assists": match["assists"],
            "yellow_cards": match["yellowCards"],
            "red_cards": match["redCards"],
            "rating": match["ratingProps"]["rating"],
            "player_of_match": match["playerOfTheMatch"],
            "started": not match["onBench"],
        })

    return recent_matches

def extract_shots(player):
    shots = player["firstSeasonStats"]["shotmap"]

    shot_data = []

    for shot in shots:
        shot_data.append({
            "event": shot["eventType"],
            "shot_type": shot["shotType"],
            "situation": shot["situation"],
            "x": shot["x"],
            "y": shot["y"],
            "minute": shot["min"],
            "period": shot["period"],
            "is_on_target": shot["isOnTarget"],
            "is_inside_box": shot["isFromInsideBox"],
            "expected_goals": shot["expectedGoals"],
            "expected_goals_on_target": shot["expectedGoalsOnTarget"],
        })

    return shot_data

player_info = extract_player_info(player)

position_info = extract_position(player)

current_season = extract_current_season(player)

season_performance = extract_season_performance(player)

career = extract_career(player)

recent_matches = extract_recent_matches(player)

shots = extract_shots(player)

player_data = {
    "info": player_info,
    "position": position_info,
    "current_season": current_season,
    "season_performance": season_performance,
    "career": career,
    "recent_matches": recent_matches,
    "shots": shots
}

print("\n===== PLAYER =====")
print(f"Name: {player_info['name']}")
print(f"Club: {player_info['club']}")
print(f"Shirt: {player_info['shirt']}")
print(f"Age: {player_info['age']}")
print(f"Preferred foot: {player_info['preferred_foot']}")
print(f"Country: {player_info['country']}")
print(f"Market value: {player_info['market_value']}")
print(f"Contract end: {player_info['contract_end']}")

print("\n===== POSITION =====")
print(f"Primary: {position_info['primary']}")

print("Secondary:")

for position in position_info["secondary"]:
    print(f"  {position}")

print("\n===== CURRENT SEASON =====")
print(f"Goals: {current_season['goals']}")
print(f"Assists: {current_season['assists']}")
print(f"Rating: {current_season['rating']}")
print(f"Matches: {current_season['matches']}")
print(f"Started: {current_season['started']}")
print(f"Minutes: {current_season['minutes']}")

print("\n===== SEASON PERFORMANCE =====")

for group_name, stats in season_performance.items():
    print(f"\n{group_name.title()}")

    for stat_name, stat_value in stats.items():
        print(f"  {stat_name}: {stat_value}")

print("\n===== CAREER =====")

for season in career:
    rating = season["rating"] if season["rating"] is not None else "N/A"

    print(
        f"{season['season']} | "
        f"{season['team']} | "
        f"{season['appearances']} apps | "
        f"{season['goals']} goals | "
        f"{season['assists']} assists | "
        f"Rating: {rating}"
    )

print("\n===== RECENT MATCHES =====")

for match in recent_matches:
    print(
        f"{match['date']} | "
        f"{match['team']} vs {match['opponent']} | "
        f"{match['score']} | "
        f"{match['minutes']} mins | "
        f"{match['goals']} goals | "
        f"{match['assists']} assists | "
        f"Rating: {match['rating']}"
    )

print("\n===== SHOTS =====")

for shot in shots:
    print(
        f"{shot['event']} | "
        f"{shot['shot_type']} | "
        f"{shot['situation']} | "
        f"xG: {shot['expected_goals']:.3f} | "
        f"Minute: {shot['minute']} | "
        f"On target: {shot['is_on_target']}"
    )