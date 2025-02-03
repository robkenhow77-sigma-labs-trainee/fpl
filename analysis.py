import json

import pandas as pd


def load_json() -> dict:
    with open('stats.json', "r", encoding="UTF-8") as file:
        return json.load(file)


def get_player_data(players: list[dict], name: str) -> dict:
    for player_data in players:
        if player_data["name"] == name:
            return player_data
    return "Player not found"


def make_player_df(player_profile: dict) -> pd.DataFrame:
    stats = player_profile["stats"]
    df = pd.DataFrame(stats)
    df["£"] = df["£"].apply(lambda x: x.replace("£", ""))
    return df



if __name__ == "__main__":
    data = load_json()
    player = "Mohamed Salah"
    player_profile = get_player_data(data, player)
    salah_df = make_player_df(player_profile)
    salah_df = salah_df.drop(labels=0)
    print(salah_df)
    average_points_per_game = salah_df["Pts"].astype(int).mean().round(2)
    print(average_points_per_game)
    
    
    
