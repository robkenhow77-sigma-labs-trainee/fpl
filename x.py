from os import path, remove
from time import sleep
import json

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def handle_cookie(driver: webdriver.Chrome) -> None:
    cookie_button = driver.find_element(By.ID, "onetrust-reject-all-handler")
    cookie_button.send_keys(Keys.RETURN)
    sleep(1)


def scroll_to_top(driver: webdriver.Chrome) -> None:
    ActionChains(driver).scroll_by_amount(0, -100000).perform()


def get_table_buttons(driver: webdriver.Chrome) -> list[WebElement]:
    buttons = driver.find_elements(By.CLASS_NAME, "ElementInTable__MenuButton-sc-y9xi40-0.eGsjiN")
    sleep(2)
    return buttons


def get_player_table(driver: webdriver.Chrome) -> WebElement:
    table = driver.find_element(By.CLASS_NAME, "Table-sc-ziussd-1.styles__HistoryTable-sc-ahs9zc-17.iPaulP.kyMyca")
    return table


def get_column_names(table: WebElement) -> list[str]:
    global column_names
    column_names = []
    header = table.find_element(By.TAG_NAME, "thead")
    headers = header.find_elements(By.TAG_NAME,"th")
    for head in headers:
        column_names.append(head.text)
    return column_names


def get_player_info(driver: WebElement) -> dict:
    name = driver.find_element(By.CLASS_NAME, "styles__ElementHeading-sc-ahs9zc-5.pMhDn")
    club = driver.find_element(By.CLASS_NAME, "styles__Club-sc-ahs9zc-6.eiknRS")
    position = driver.find_element(By.CLASS_NAME, "styles__ElementTypeLabel-sc-ahs9zc-4.gjUdZJ")
    print(name.text)
    return {"name": name.text,
            "position": position.text, 
            "club": club.text}


def get_player_stats(table: WebElement) -> list[dict]:
    player = []
    table_body = table.find_element(By.TAG_NAME, "tbody")
    rows = table_body.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        week = {}
        stats = row.find_elements(By.TAG_NAME, "td")
        for i in range(len(stats)):
            week[column_names[i]] = stats[i].text
        player.append(week)
    return player


def exit_table(driver: webdriver.Chrome) -> None:
    exit = driver.find_element(By.CLASS_NAME, "Dialog__CloseButton-sc-5bogmv-1.gthsYI")
    exit.click()


def get_stats_for_page(driver: webdriver.Chrome, num_players) -> list:
    global got_column_names
    global column_names
    buttons = get_table_buttons(driver)
    players = []
    for button in buttons[:num_players]:
        button.click()
        sleep(0.5)
        table = get_player_table(driver)
        player_info = get_player_info(driver)
        sleep(1)

        if not got_column_names:
            column_names = get_column_names(table)
            got_column_names = True

        stats = get_player_stats(table)
        player_info["stats"] = stats
        players.append(player_info)
        exit_table(driver)

    return players


def get_page_number(driver: webdriver.Chrome) -> int:
    status = driver.find_elements(By.XPATH, "//div[@role='status' and @aria-live='polite']")[-1]
    page_number = int(status.text.split("of")[0].strip())
    return page_number


def change_page(driver: webdriver.Chrome) -> None:
    buttons = driver.find_elements(By.CLASS_NAME, "PaginatorButton__Button-sc-xqlaki-0.cmSnxm")
    buttons[-1].click()
    sleep(2)


def make_file(all_stats: list[list[dict]]) -> None:
    if path.exists('stats.json'):
        remove('stats.json')
    with open('stats.json', 'x', encoding="UTF-8") as file:
        json.dump(all_stats, file, indent=4)


def get_all_stats(driver: webdriver.Chrome, num_pages, num_players):
    status = driver.find_elements(By.XPATH, "//div[@role='status' and @aria-live='polite']")[-1]
    number_of_pages = int(status.text.split("of")[-1].strip())

    all_stats = []
    scraping = True

    while scraping:
        page_number = get_page_number(driver)
        stats = get_stats_for_page(driver, num_players)
        all_stats.extend(stats)
        change_page(driver)
        scroll_to_top(driver)

        if page_number == num_pages:
            scraping = False

    make_file(all_stats)


if __name__ == "__main__":
    chrome_driver = webdriver.Chrome()
    chrome_driver.get("https://fantasy.premierleague.com/statistics")
    sleep(2)
    handle_cookie(chrome_driver)
    column_names = []
    got_column_names = False
    number_of_pages_to_scrape = 1
    number_of_players_per_page = 2
    get_all_stats(chrome_driver, number_of_pages_to_scrape, number_of_players_per_page)

    chrome_driver.quit()