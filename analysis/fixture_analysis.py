from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import psycopg
import pandas as pd
from psycopg.rows import dict_row


def init_driver():
    driver = webdriver.Chrome()
    driver.get("https://fantasy.premierleague.com/fixtures/25")
    sleep(2)
    return driver


def handle_cookie(driver: webdriver.Chrome) -> None:
    cookie_button = driver.find_element(By.ID, "onetrust-reject-all-handler")
    cookie_button.send_keys(Keys.RETURN)
    sleep(1)


def get_fixtures():
    driver = init_driver()
    handle_cookie(driver)
    teams = driver.find_elements(By.CLASS_NAME, "styles__TeamName-sc-od3kjq-4.eMFDti")
    fixtures = []
    for i, team in enumerate(teams):
        if i % 2 == 0:
            fixture = []
            fixture.append(team.text)
            fixtures.append(fixture)
        else:
            fixture.append(team.text)
    return fixtures


def get_team_data(conn: psycopg.Connection):
    sql = """
    select * from team
    left join league using (team_id);        
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql)
        return cur.fetchall()


def clean_ratings_dict(ratings: dict) -> dict:
    return {
        'Brighton': ratings['Brighton & Hove Albion'], 
        'Chelsea': ratings['Chelsea'], 
        'Leicester': ratings['Leicester City'],
        'Arsenal': ratings['Arsenal'],
        'Aston Villa': ratings['Aston Villa'],
        'Ipswich': ratings['Ipswich Town'],
        'Fulham': ratings['Fulham'],
        "Nott'm Forest": ratings['Nottingham Forest'],
        'Man City': ratings['Manchester City'],
        'Newcastle': ratings['Newcastle United'],
        'Southampton': ratings['Southampton'],
        'Bournemouth': ratings['Bournemouth'], 
        'West Ham': ratings['West Ham United'],
        'Brentford': ratings['Brentford'],
        'Crystal Palace': ratings['Crystal Palace'],
        'Everton': ratings['Everton'],
        'Liverpool': ratings['Liverpool'],
        'Wolves': ratings['Wolverhampton Wanderers'], 
        'Spurs': ratings['Tottenham Hotspur'],
        'Man Utd': ratings['Manchester United']
    }


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
    ratings_dict = clean_ratings_dict(ratings_dict)
    df = pd.DataFrame({"home_team": home, "away_team": away})
    df["home_rating"] = df["home_team"].apply(lambda x: ratings_dict[x] * 1.2)
    df["away_rating"] = df["away_team"].apply(lambda x: ratings_dict[x] * 0.8)
    df["prediction"] = df.apply(lambda row: 
        "draw" if abs(row["home_rating"] - row["away_rating"]) < 1
        else row["home_team"] if row["home_rating"] > row["away_rating"]
        else row["away_team"],
        axis=1)
    
    return df


def get_fixture_predictions(conn: psycopg.Connection):
    match_fixtures = get_fixtures()
    team_data = get_team_data(conn)
    team_df = pd.DataFrame(team_data)
    team_ratings_df = team_ratings(team_df)
    return predict_fixtures(team_ratings_df, match_fixtures)


if __name__ == "__main__":
    conn_string = "postgresql:///fantasy_football?host=localhost"
    connection = psycopg.connect(conn_string)

    predictions = get_fixture_predictions(connection)
    print(predictions)

    connection.close()
