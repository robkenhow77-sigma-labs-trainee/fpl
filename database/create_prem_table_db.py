import psycopg
import pandas as pd
from time import sleep

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from player_and_gameweek import map_club


def handle_cookie(driver: webdriver.Chrome) -> None:
    cookie_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='reject-button']")
    cookie_button.send_keys(Keys.RETURN)
    sleep(1)


def get_table_html(driver: webdriver.Chrome) -> list[str]:
    """Gets the premier league data from BBC sport,
    returns a list of strings containing the data as a list of strings."""
    team_data = []
    table = driver.find_element(By.TAG_NAME, 'table')
    teams = table.find_elements(By.TAG_NAME, 'tbody')
    for row in teams:
        tr = row.find_elements(By.TAG_NAME, 'tr')
        for td in tr:
            data = []
            for content in td.find_elements(By.TAG_NAME, 'td'):
                data.append(content.text)
            team_data.append(data)
    return team_data


def format_table(teams_data: list[str]) -> dict:
    """Takes a list of strings and creates a dictionary for each team."""
    teams_dicts = []
    for data in teams_data:
        form =  format_form(data[10])
        teams_dicts.append({
            "position": data[0],
            "team_id": map_club(data[1]),
            "played": data[2],
            "won": data[3],
            "drawn": data[4],
            "lost": data[5],
            "goals For": data[6],
            "goals Against": data[7],
            "goal difference": data[8],
            "points": data[9],
            "previous game": form[0],
            "game -2": form[1],
            "game -3": form[2],
            "game -4": form[3],
            "game -5": form[4],
            "game -6": form[5],
            })
    return teams_dicts


def format_form(current_form: str) -> list[dict]:
    """Takes a list of strings and creates a dictionary for each team, showing their recent form."""  
    current_form = current_form.lower().replace('result', '')
    current_form = current_form.replace(
        "\n", "").replace("win", "").replace("loss", "").replace("draw", "").strip()
    results = current_form.split(' ')
    return results[::-1]


def make_table_data_for_db(table_dicts: list[dict]):
    teams = []
    for row in table_dicts:
        teams.append(
        (row['team_id'], row['position'], row['played'],
        row['won'], row['drawn'], row['lost'],
        row['goals For'], row['goals Against'], row['goal difference'],
        row['points'], row['previous game'], row['game -2'],
        row['game -3'], row['game -4'], row['game -5'], row['game -6']
        ))
    return teams


def insert_data_to_db(conn: psycopg.Connection, table_data: list[tuple]):
    sql = """
        INSERT INTO league
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    with conn.cursor() as cur:
        cur.executemany(sql, table_data)
        conn.commit()


if __name__ == "__main__":
    conn_string = "postgresql:///fantasy_football?host=localhost"
    connection = psycopg.connect(conn_string)
    url = "https://www.bbc.co.uk/sport/football/premier-league/table"
    web_driver = webdriver.Chrome()
    web_driver.get(url)
    sleep(2)
    handle_cookie(web_driver)
    table_data = get_table_html(web_driver)
    table_data = format_table(table_data)
    table_data_for_db = make_table_data_for_db(table_data)
    insert_data_to_db(connection, table_data_for_db)
    connection.close()
