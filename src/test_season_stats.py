import requests
import sys


def get_player_data(player_id):
    url = "https://www.fotmob.com/api/data/playerData"

    params = {
        "id": player_id
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()


def find_season_id(player, season_name):
    for season in player["statSeasons"]:
        if season["seasonName"] != season_name:
            continue

        for tournament in season["tournaments"]:
            if tournament["hasDeepStats"]:
                return tournament["entryId"]

    return None


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


def print_stats(stats):
    print("\n===== TOP STAT CARD =====")

    for stat in stats["topStatCard"]["items"]:
        print(
            f"{stat['title']}: "
            f"total={stat['statValue']} | "
            f"per90={stat['per90']}"
        )

    print("\n===== SEASON PERFORMANCE =====")

    for group in stats["statsSection"]["items"]:
        print(f"\n{group['title']}")

        for stat in group["items"]:
            print(
                f"  {stat['title']}: "
                f"total={stat['statValue']} | "
                f"per90={stat['per90']}"
            )


def main():
    player_id = sys.argv[1]
    season_name = sys.argv[2]

    player = get_player_data(player_id)

    print(f"Player: {player['name']}")
    print(f"Requested season: {season_name}")

    season_id = find_season_id(player, season_name)

    if season_id is None:
        print(f"\nNo deep stats found for season: {season_name}")
        sys.exit(1)

    print(f"Found season ID: {season_id}")

    stats = get_season_stats(player_id, season_id)

    print_stats(stats)


if __name__ == "__main__":
    main()