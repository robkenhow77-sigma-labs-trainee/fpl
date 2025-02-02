from os import path, remove
from time import sleep

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def handle_cookie(driver: webdriver.Chrome) -> None:
    cookie_button = driver.find_element(By.ID, "onetrust-reject-all-handler")
    cookie_button.send_keys(Keys.RETURN)
    sleep(1)


def get_table_buttons(driver: webdriver.Chrome) -> list[WebElement]:
    buttons = driver.find_elements(By.CLASS_NAME, "ElementInTable__MenuButton-sc-y9xi40-0.eGsjiN")
    return buttons


def get_player_table(driver: webdriver.Chrome) -> WebElement:
    table = driver.find_element(By.CLASS_NAME, "Table-sc-ziussd-1.styles__HistoryTable-sc-ahs9zc-17.iPaulP.kyMyca")
    return table


def get_column_names(table: WebElement) -> list[str]:
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


def get_player_stats(table: WebElement, column_names: list[str]) -> list[dict]:
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


def get_stats_for_page(driver: webdriver.Chrome, got_column_names: bool) -> list:
    buttons = get_table_buttons(driver)
    sleep(10)    
    players = []
    for button in buttons[:1]:
        button.click()
        sleep(0.5)
        table = get_player_table(driver)
        player_info = get_player_info(driver)
        if not got_column_names:
            columns = get_column_names(table)
            got_column_names = True
        stats = get_player_stats(table, columns)
        stats.insert(0, player_info)
        players.append(stats)
        exit_table(driver)
    return players


def get_page_number(driver: webdriver.Chrome) -> int:
    status = driver.find_elements(By.XPATH, "//div[@role='status' and @aria-live='polite']")[-1]
    page_number = int(status.text.split("of")[0].strip())
    return page_number


def change_page(driver: webdriver.Chrome) -> None:
    button = driver.find_element(By.CLASS_NAME, "PaginatorButton__Button-sc-xqlaki-0.cmSnxm")
    button.click()
    sleep(1)


def make_file(all_stats: list[list[dict]]) -> None:
    if path.exists('stats.txt'):
        remove('stats.txt')
    with open('stats.txt', 'x', encoding="UTF-8") as file:
        file.writelines(all_stats)


def get_all_stats(driver: webdriver.Chrome, column_names: bool):
    status = driver.find_elements(By.XPATH, "//div[@role='status' and @aria-live='polite']")[-1]
    number_of_pages = int(status.text.split("of")[-1].strip())

    all_stats = []
    scraping = True

    while scraping:
        page_number = get_page_number(driver)
        print("ahh")
        stats = get_stats_for_page(driver, column_names)
        all_stats.extend(stats)
        change_page(driver)

        if page_number == number_of_pages:
            scraping = False


if __name__ == "__main__":
    chrome_driver = webdriver.Chrome()
    chrome_driver.get("https://fantasy.premierleague.com/statistics")
    sleep(2)
    handle_cookie(chrome_driver)

    got_columns = False
    get_all_stats(chrome_driver, got_columns)

    chrome_driver.quit()