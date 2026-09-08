import requests
import sys
import pandas as pd
import re

def get_player_data(player_id):
    url = f"https://www.fotmob.com/api/data/playerData?id={player_id}"

    response = requests.get(url)
    response.raise_for_status()

    return response.json()


def get_season_stats(player_id, season_id):
    url = "https://www.fotmob.com/api/data/playerStats"

    params = {
        "playerId": player_id,
        "seasonId": season_id,
        "isFirstSeason": "false",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()

def get_season_stats(player_id, entry_id):
    url = (
        f"https://www.fotmob.com/api/data/playerStats"
        f"?playerId={player_id}"
        f"&seasonId={entry_id}"
        f"&isFirstSeason=false"
    )

    response = requests.get(url)
    response.raise_for_status()

    return response.json()

def extract_deep_season_stats(stats):
    performance = {}

    for group in stats["statsSection"]["items"]:
        group_name = group["title"].lower()

        performance[group_name] = {}

        for stat in group["items"]:
            performance[group_name][stat["title"]] = {
                "total": stat["statValue"],
                "per90": stat.get("per90"),
            }

    return performance

def flatten_season_stats(deep_stats):
    flat_stats = {}

    for group_name, stats_group in deep_stats.items():
        for stat_name, values in stats_group.items():

            key = stat_name.lower().replace(" ", "_")

            flat_stats[f"{key}_total"] = values["total"]
            flat_stats[f"{key}_per90"] = values["per90"]

    return flat_stats

def build_scouting_record(flat_stats, player_info, position_info, selected_season):
    selected_stats = [
        "goals_total",
        "goals_per90",
        "penalty_goals_total",
        "shots_total",
        "shots_per90",
        "shots_on_target_total",
        "shots_on_target_per90",
        "assists_total",
        "assists_per90",
        "accurate_passes_total",
        "accurate_passes_per90",
        "pass_accuracy_total",
        "pass_accuracy_per90",
        "duels_won_total",
        "duels_won_per90",
        "duels_won_pct_total",
        "duels_won_pct_per90",
        "aerials_won_total",
        "aerials_won_per90",
        "aerials_won_pct_total",
        "aerials_won_pct_per90",
        "touches_total",
        "touches_per90",
        "touches_in_opposition_box_total",
        "touches_in_opposition_box_per90",
        "fouls_won_total",
        "fouls_won_per90",
        "defensive_actions_total",
        "defensive_actions_per90",
        "blocked_scoring_attempt_total",
        "blocked_scoring_attempt_per90",
        "fouls_committed_total",
        "fouls_committed_per90",
        "recoveries_total",
        "recoveries_per90",
        "dribbled_past_total",
        "dribbled_past_per90",
        "clean_sheets_total",
        "clean_sheets_per90",
        "goals_conceded_while_on_pitch_total",
        "goals_conceded_while_on_pitch_per90",
        "yellow_cards_total",
        "red_cards_total",
    ]

    record = {
        "player_id": flat_stats["player_id"],
        "player": player_info["name"],
        "season": selected_season["season"],
        "competition": selected_season["tournament"],
        "position": position_info["primary"],
    }

    for stat in selected_stats:
        value = flat_stats.get(stat)

        if isinstance(value, (int, float)):
            value = round(value, 2)

        record[stat] = value

    return record

def extract_season_summary(stats):
    summary = {}

    for stat in stats["topStatCard"]["items"]:
        summary[stat["title"]] = {
            "total": stat["statValue"],
            "per90": stat.get("per90"),
        }

    return summary

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


def extract_stat_seasons(player):
    seasons = []

    for season in player["statSeasons"]:
        for tournament in season["tournaments"]:
            seasons.append({
                "season": season["seasonName"],
                "tournament": tournament["name"],
                "tournament_id": tournament["tournamentId"],
                "entry_id": tournament["entryId"],
                "has_deep_stats": tournament["hasDeepStats"],
            })

    return seasons


def select_season(stat_seasons):
    print("\n===== AVAILABLE STAT SEASONS =====")

    for index, season in enumerate(stat_seasons, start=1):
        print(
            f"{index}. "
            f"{season['season']} | "
            f"{season['tournament']} | "
            f"Deep stats: {season['has_deep_stats']}"
        )

    while True:
        choice = input("\nSelect a season: ")

        try:
            choice = int(choice)

            if 1 <= choice <= len(stat_seasons):
                return stat_seasons[choice - 1]

        except ValueError:
            pass

        print("Invalid selection. Please enter one of the numbers above.")


def extract_season_performance(stats):
    performance = {}

    for group in stats["statsSection"]["items"]:
        group_name = group["title"].lower()

        performance[group_name] = {}

        for stat in group["items"]:
            performance[group_name][stat["title"]] = {
                "total": stat["statValue"],
                "per90": stat["per90"],
            }

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
            "rating": season["rating"].get("rating")
            if season.get("rating")
            else None,
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


def build_player_data(player):
    player_info = extract_player_info(player)
    position_info = extract_position(player)
    stat_seasons = extract_stat_seasons(player)
    career = extract_career(player)
    recent_matches = extract_recent_matches(player)
    shots = extract_shots(player)

    return {
        "info": player_info,
        "position": position_info,
        "stat_seasons": stat_seasons,
        "career": career,
        "recent_matches": recent_matches,
        "shots": shots,
    }

def main():
    player_id = sys.argv[1]

    player = get_player_data(player_id)

    player_data = build_player_data(player)

    player_info = player_data["info"]
    position_info = player_data["position"]
    career = player_data["career"]
    recent_matches = player_data["recent_matches"]
    stat_seasons = player_data["stat_seasons"]

    print("\n===== AVAILABLE STAT SEASONS =====")

    for season in stat_seasons:
        print(
            f"{season['season']} | "
            f"{season['tournament']} | "
            f"Entry ID: {season['entry_id']} | "
            f"Deep stats: {season['has_deep_stats']}"
        )

    entry_id = input("\nEnter season Entry ID: ").strip()

    selected_season = next(
        (
            season
            for season in stat_seasons
            if season["entry_id"] == entry_id
        ),
        None
    )

    if selected_season is None:
        print(f"\nInvalid Entry ID: {entry_id}")
        return

    print(
        f"\nFetching deep stats for "
        f"{selected_season['season']} — "
        f"{selected_season['tournament']}..."
    )

    stats = get_season_stats(player_id, entry_id)

    season_summary = extract_season_summary(stats)
    deep_stats = extract_deep_season_stats(stats)
    flat_stats = flatten_season_stats(deep_stats)

    flat_stats["player_id"] = player_id

    flat_stats["duels_won_pct_total"] = flat_stats.pop(
        "duels_won_%_total", None
    )
    flat_stats["duels_won_pct_per90"] = flat_stats.pop(
        "duels_won_%_per90", None
    )
    flat_stats["aerials_won_pct_total"] = flat_stats.pop(
        "aerials_won_%_total", None
    )
    flat_stats["aerials_won_pct_per90"] = flat_stats.pop(
        "aerials_won_%_per90", None
    )

    scouting_record = build_scouting_record(
        flat_stats,
        player_info,
        position_info,
        selected_season,    
    )

    df = pd.DataFrame([scouting_record])

    player_name = re.sub(r"[^A-Za-z0-9]+", "_", player_info["name"]).strip("_")
    filename = f"{player_name}_scouting_report.csv"

    if pd.io.common.file_exists(filename):
        existing_df = pd.read_csv(filename)

        df = pd.concat([existing_df, df], ignore_index=True)

        df["_season_order"] = (
            df["season"]
            .astype(str)
            .str.extract(r"(\d{2})")[0]
            .astype(int)
        )

        df = (
            df.sort_values("_season_order")
            .drop(columns="_season_order")
            .reset_index(drop=True)
        )

    df.to_csv(
        filename,
        index=False,
    )

    print(f"\n===== CSV RECORD SAVED =====")
    print(f"File: {filename}")
    print(df.to_string(index=False))

    print("\n===== CSV RECORD SAVED =====")
    print(df.to_string(index=False))

    print("\n===== FLAT STATS =====")

    for stat_name, value in flat_stats.items():
        print(f"{stat_name}: {value}")

    print("\n===== SELECTED SEASON =====")
    print(f"Season: {selected_season['season']}")
    print(f"Tournament: {selected_season['tournament']}")
    print(f"Entry ID: {selected_season['entry_id']}")

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

if __name__ == "__main__":
    main()