import json


def get_players():
    with open("season_stats/players.json", "r", encoding="UTF-8") as file:
        return json.load(file)


def extract_info(data: list[dict]):
    for row in data:
        


if __name__ == "__main__":
    players = get_players()
    print(players)