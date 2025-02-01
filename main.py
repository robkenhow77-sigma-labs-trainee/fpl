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


def init_argsparse():
    parser = ArgumentParser()
    parser.add_argument("-s", "--scrape", action="store_true", help="Activates the scraper to create a new text file.")
    args = parser.parse_args()
    return args.scrape


def get_players_from_internet() -> list[dict]:
    players_names_and_links = []
    driver = webdriver.Chrome()
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


def create_players_json(players_list: list[str]) -> None:
    if path.exists('players.json'):
        remove('players.json')

    with open("players.json", 'x', encoding="UTF-8") as file:
        json.dump(players_list, file, indent=4)


def get_players_from_json() -> list[dict]:
    with open("players.json", "r", encoding="UTF-8") as file:
        players_list = json.load(file)
        return players_list


def get_stats(url: str) -> dict[dict]:
    statistics = {}
    url = url.replace("overview", "stats?co=1&se=719")
    res = get(url).text
    soup = BeautifulSoup(res, 'html.parser')
    tables = soup.find_all(class_ = "player-stats__stat")
    for table in tables:
        stat_type = table.find(class_= "player-stats__stat-title").text
        stats = table.find_all(class_ = "player-stats__stat-value")
        profile = {}
        for stat in stats:
            stat_name = stat.text.split("\n")[0].strip()
            statistic = stat.text.split("\n")[1].strip()
            profile[stat_name] = statistic
        statistics[stat_type] = profile
    return statistics


def add_stats_to_player(players_list: list[dict]) -> list[dict]:
    for player in players_list:
        url = player["link"]
        player["stats"] = get_stats(url)
        print(player["name"])
    return players_list


if __name__ == "__main__":
    # Initialise
    scraping = init_argsparse()

    # If scraping, get the data and create a json. Otherwise get data from json.
    if scraping:
        players = get_players_from_internet()
        players = add_stats_to_player(players)
        create_players_json(players)
    else:
        players = get_players_from_json()
   

    
    

