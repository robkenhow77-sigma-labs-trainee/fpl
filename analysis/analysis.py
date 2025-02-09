import psycopg
import pandas as pd
from psycopg.rows import dict_row

from fixtures import get_fixtures


def get_team_data(conn: psycopg.Connection):
    sql = """
    select * from team
    left join league using (team_id);        
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql)
        return cur.fetchall()


def team_ratings(df: pd.DataFrame):
    df = df[["team_name", "league_position", "previous_game", "game_2",
           "game_3", "game_4", "game_5", "game_6"]].copy()
    df["league_position"] = df["league_position"].apply(lambda x: (21 - x)/5)
    df[["previous_game", "game_2"]] = df[["previous_game", "game_2"]].replace({"w": 3, "d": 0, "l": -3})
    df[["game_3", "game_4"]] = df[["game_3", "game_4"]].replace({"w": 2, "d": 0, "l": -2})
    df[["game_5", "game_6"]] = df[["game_5", "game_6"]].replace({"w": 1, "d": 0, "l": -1})
    df["form"] = df[["previous_game", "game_2", "game_3", "game_4", "game_5", "game_6"]].sum(axis=1)
    df["rating"] = df[["form", "league_position"]].sum(axis=1).round(2)
    df = df[["team_name", "rating"]]
    return df


def predict_fixtures(ratings: pd.DataFrame, fixtures: list[list]):
    home = [team[0] for team in fixtures]
    away = [team[1] for team in fixtures]
    ratings_dict = ratings.to_dict(orient='records')
    ratings_dict = {rating["team_name"]: rating["rating"] for rating in ratings_dict}
    df = pd.DataFrame( {"home_team": home, "away_team": away} )

    print(df)



if __name__ == "__main__":
    conn_string = "postgresql:///fantasy_football?host=localhost"
    connection = psycopg.connect(conn_string)
    match_fixtures = get_fixtures()
    team_data = get_team_data(connection)
    team_df = pd.DataFrame(team_data)
    team_ratings_df = team_ratings(team_df)
    print(predict_fixtures(team_ratings_df, match_fixtures))
    
