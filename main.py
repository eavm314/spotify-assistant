from src.config import init_spotify
from src.menu import *
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOauthError

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
    try:
        current_user = init_spotify()
    except RuntimeError as e:
        print(f"Configuration error: {e}")
        exit(1)
    except SpotifyOauthError as e:
        print(f"Spotify authentication failed: {e}")
        print("Check SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET in .env, and make sure "
              "the redirect URI http://127.0.0.1:9090 is registered in your Spotify app settings.")
        exit(1)
    except SpotifyException as e:
        print(f"Error initializing Spotify client: {e.msg}")
        exit(1)

    print(f"Welcome, {current_user['display_name']}!")
    menu()