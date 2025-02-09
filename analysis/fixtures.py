from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


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


if __name__ == "__main__":
    fixtures = get_fixtures()
