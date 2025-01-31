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


def get_players_from_internet():
    players = []
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
    driver.quit()

    players_names = driver.find_elements(By.CLASS_NAME, "player")

    for player in players_names:
        name = player.find_element(By.TAG_NAME, "a").text
        link = player.find_element(By.TAG_NAME,'a').get_attribute("href")
        players.append({"name": name, "link": link})
    return players


def create_players_text_file(players: list[str]) -> None:
    if path.exists('players.json'):
        remove('players.json')

    with open("players.json", 'x', encoding="UTF-8") as file:
        json.dump(players, file, indent=4)


def get_players_from_json():
    with open("players.txt", "r", encoding="UTF-8") as file:
        players = json.load(file)
        return players


def clean_names(players: list[dict]):
    for player in players:
        player["name"] = player["name"].encode('latin1').decode('utf-8')
    return players


if __name__ == "__main__":
    new_players = init_argsparse()
    if new_players:
        player_names = get_players_from_internet()
        create_players_text_file(player_names)
    player_names = get_players_from_json()
    player_names = clean_names(player_names)
    print(player_names)
