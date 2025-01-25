from src.config import username, password
from selenium.webdriver import Chrome, ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

spotify_url = 'https://open.spotify.com/'

def create_group_playlist_folders():
    webdriver_service = ChromeService(executable_path='drivers/chromedriver.exe')
    driver = Chrome(service=webdriver_service)
    driver.implicitly_wait(10)

    driver.get(spotify_url)

    login_button = driver.find_element(By.XPATH, '//button[@data-testid="login-button"]')
    login_button.click()

    username_input = driver.find_element(By.XPATH, '//input[@data-testid="login-username"]')
    username_input.send_keys(username)

    password_input = driver.find_element(By.XPATH, '//input[@data-testid="login-password"]')
    password_input.send_keys(password)

    login_button = driver.find_element(By.ID, 'login-button')
    login_button.click()
    
    user_widget = driver.find_element(By.XPATH, '//button[@data-testid="user-widget-link"]')
    assert user_widget.get_attribute('aria-label') == 'Enrique Vicente'
    driver.close()