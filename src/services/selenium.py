from selenium.webdriver import Chrome, ChromeService, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from src.config import username, password
from src.services import get_groups, get_playlists_by_group
from src.entities import Playlist

spotify_url = 'https://open.spotify.com/'

def sync_group_playlist_folders():
    driver = config_driver()

    driver.get(spotify_url)
    login(driver)

    groups = get_groups()
    if len(groups) == 0:
        print("No groups to sync folders for")
        return
    for group in groups:
        print(f"Syncing folder for group '{group.key}'...")
        create_playlist_folder(driver, group.name)
        playlists = get_playlists_by_group(group.key)

        for playlist in playlists:
            add_playlist_to_folder(driver, playlist, group.name)
    
    driver.close()


def config_driver():
    webdriver_service = ChromeService(executable_path='drivers/chromedriver.exe')
    driver = Chrome(service=webdriver_service)
    driver.implicitly_wait(10)
    return driver


def login(driver: Chrome):
    login_button = driver.find_element(By.XPATH, '//button[@data-testid="login-button"]')
    login_button.click()

    username_input = driver.find_element(By.XPATH, '//input[@data-testid="login-username"]')
    username_input.send_keys(username)

    password_input = driver.find_element(By.XPATH, '//input[@data-testid="login-password"]')
    password_input.send_keys(password)

    login_button = driver.find_element(By.ID, 'login-button')
    login_button.click()

    cookies_close = driver.find_element(By.ID, 'onetrust-close-btn-container')
    cookies_close.click()


def create_playlist_folder(driver: Chrome, folder_name: str):
    try:
        driver.find_element(By.XPATH, f'//span[text()="{folder_name}"]')
        return
    except NoSuchElementException:
        print(f"Creating folder '{folder_name}'...")

    create_button = driver.find_element(By.XPATH, '//button[@aria-label="Create playlist or folder"]')
    create_button.click()
    create_folder_option = driver.find_element(By.XPATH, '//span[text()="Create a playlist folder"]')
    create_folder_option.click()

    new_folder = driver.find_element(By.XPATH, '//span[text()="New Folder"]')
    actions = ActionChains(driver)
    actions.context_click(new_folder).perform()

    rename_button = driver.find_element(By.XPATH, '//span[text()="Rename"]')
    rename_button.click()

    folder_name_input = driver.find_element(By.XPATH, '//input[@value="New Folder"]')
    folder_name_input.clear()
    folder_name_input.send_keys(folder_name)

    save_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    save_button.click()


def add_playlist_to_folder(driver: Chrome, playlist: Playlist, folder_name: str):
    try:
        playlist_element = driver.find_element(By.XPATH, f'//span[text()="{playlist.name}"]/../..')
    except NoSuchElementException:
        return
    
    print(f"Adding playlist '{playlist.name}' to folder '{folder_name}'...")
    actions = ActionChains(driver)
    actions.context_click(playlist_element).perform()

    add_to_playlist_option = driver.find_element(By.XPATH, '//span[text()="Move to folder"]')
    add_to_playlist_option.click()

    folder = driver.find_element(By.XPATH, f'//button/span[text()="{folder_name}"]')
    folder.click()

    WebDriverWait(driver, 10).until(EC.staleness_of(playlist_element))