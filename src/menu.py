from src.config import execute_raw_query, spotify
from src.services import *


def exit_menu():
    print("Goodbye!")
    exit()


def sync_all_menu():
    sync_all_new_content()
    

def sync_playlists_by_group_menu():
    sync_playlists_by_group()


def sync_new_followed_artists_menu():
    sync_new_followed_artists()


def sync_new_saved_tracks_menu():
    sync_new_saved_tracks_to_playlists()


def sync_playlist_deletions_menu():
    sync_playlist_deletions()


def delete_playlists_by_group_menu():
    group_key = input("Enter the group key: ").strip()
    delete_playlists_by_group(group_key)

# def selenium_menu():
#     sync_group_playlist_folders()