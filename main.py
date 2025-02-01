"""FPL web scraper"""
from argparse import ArgumentParser
from os import remove, path
import json

from time import sleep
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options


def init_argsparse():
    """Gets argparse arguments."""
    parser = ArgumentParser()
    parser.add_argument("-s", "--scrape", action="store_true", help="Activates the scraper to create a new text file.")
    args = parser.parse_args()
    return args.scrape


def get_players_from_internet(options: Options) -> list[dict]:
    """Gets the players names anf the link of their stats page."""
    players_names_and_links = []
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.premierleague.com/players")
    sleep(2)
    button = driver.find_element(By.ID, "onetrust-reject-all-handler")
    button.send_keys(Keys.RETURN)
    footer = driver.find_element(By.TAG_NAME, "footer")

    for _ in range(20):
        ActionChains(driver).scroll_to_element(footer).perform()
        sleep(1)
        ActionChains(driver).scroll_by_amount(0,-500).perform()
        sleep(1)
    

    players_names = driver.find_elements(By.CLASS_NAME, "player")

    for player in players_names:
        name = player.find_element(By.TAG_NAME, "a").text
        link = player.find_element(By.TAG_NAME,'a').get_attribute("href")
        position = player.find_element(By.CLASS_NAME, "u-hide-mobile-lg.player__position").text
        players_names_and_links.append({"name": name, "link": link, "position": position})
    driver.quit()
    return players_names_and_links


def create_players_json(filename: str, players_list: list[str]) -> None:
    """Creates a json from the players data."""
    if path.exists(filename):
        remove(filename)

    with open(filename, 'x', encoding="UTF-8") as file:
        json.dump(players_list, file, indent=4)


def get_players_from_json(filename: str) -> list[dict]:
    """Gets the players data from the json"""
    with open(filename, "r", encoding="UTF-8") as file:
        players_list = json.load(file)
        return players_list


def get_stats(url: str, driver: webdriver) -> dict[dict]:
    statistics = {}
    url = url.replace("overview", "stats?co=1&se=719")
    driver.get(url)
    sleep(3)
    tables = driver.find_elements(By.CLASS_NAME, "player-stats__stat")
    for table in tables:
        # stat_type = table.find(class_= "player-stats__stat-title").text
        stats = table.find_elements(By.CLASS_NAME, "player-stats__stat-value")
        for stat in stats:
            stat_name = stat.text.split("\n")[0].strip()
            statistic = stat.text.split("\n")[1].strip()
            statistics[stat_name] = statistic
    return statistics


def add_stats_to_player(players_list: list[dict], options: Options) -> list[dict]:
    driver = webdriver.Chrome(options=options)
    for player in players_list:
        url = player["link"]
        stats = get_stats(url, driver)
        for stat in stats.keys():
            player[stat] = stats[stat]
        print(player["name"])
    driver.quit()
    return players_list


def create_dataframes(players_list: list[dict]) -> tuple[pd.DataFrame]:
    df_goalkeepers = pd.DataFrame([player for player in players_list if player["position"] == "Goalkeeper"]).drop(columns='link')
    df_defenders = pd.DataFrame([player for player in players_list if player["position"] == "Defender"]).drop(columns='link')
    df_midfielders = pd.DataFrame([player for player in players_list if player["position"] == "Midfielder"]).drop(columns='link')
    df_forwards = pd.DataFrame([player for player in players_list if player["position"] == "Forward"]).drop(columns='link')
    return df_goalkeepers, df_defenders, df_midfielders, df_forwards


if __name__ == "__main__":
    # Initialise
    scraping = init_argsparse()
    file = "players.json"
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Getting/creating the data
    if scraping:
        players = get_players_from_internet(chrome_options)
        players = add_stats_to_player(players, chrome_options)
        create_players_json(file, players)
    else:
        players = get_players_from_json(file)
    
    # Create dataframes
    goalkeepers_df, defenders_df, midfielders_df, forwards_df = create_dataframes(players)

    # top 10 highest scorers forwards
    goals_df = forwards_df[["name", "Goals"]]
    goals_df = goals_df.dropna()
    goals_df["Goals"] = goals_df["Goals"].astype(int)
    print(goals_df.sort_values('Goals'))
    
    # top 5 clean sheets keepers, defenders
    # most assists midfielders




   

    
    
    

    
   

    
    

