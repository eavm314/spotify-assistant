from src.config import current_user
from src.menu import *

options = {
    '1': sync_playlists_by_group_menu,
    '2': delete_playlists_by_group_menu,
    '3': selenium_menu,
    '9': exit_menu
}

def menu():
    while True:
        print("----------------------------------")
        print("Spotify Assistant Menu")
        print("1. Sync playlists by group")
        print("2. Delete playlists by group")
        print("3. Selenium folder creation")
        print("9. Exit")
        print("----------------------------------")

        option = input("Choose an option: ").strip()
        if option not in options:
            print("Invalid option.")
        else:
            options[option]()
    

if __name__ == '__main__':
    print(f"Welcome, {current_user['display_name']}!")
    menu()