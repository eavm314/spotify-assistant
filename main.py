from src.config import current_user
from src.menu import *

options = {
    '1': sync_all_menu,
    '2': sync_new_followed_artists_menu,
    '3': sync_new_saved_tracks_menu,
    '4': delete_playlists_by_group_menu,
    '9': exit_menu
}

def menu():
    while True:
        print("----------------------------------")
        print("Spotify Assistant Menu")
        print("1. Sync All (New Content)")
        print("2. Sync new followed artists")
        print("3. Sync new saved tracks to playlists")
        print("4. Delete playlists by group")
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