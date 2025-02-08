from time import sleep

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


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
            "name": data[1],
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


def make_table_df():
    url = "https://www.bbc.co.uk/sport/football/premier-league/table"
    web_driver = webdriver.Chrome()
    web_driver.get(url)
    sleep(2)
    handle_cookie(web_driver)
    table_data = get_table_html(web_driver)
    table_data = format_table(table_data)
    return pd.DataFrame(table_data)


if __name__ == "__main__":
    table_df = make_table_df()
    print(table_df)
