from src.config import execute_raw_query, spotify
from src.services import *


def exit_menu():
    print("Goodbye!")
    exit()


def sync_playlists_by_group_menu():
    sync_playlists_by_group()


def delete_playlists_by_group_menu():
    group_key = input("Enter the group key: ").strip()
    delete_playlists_by_group(group_key)

def selenium_menu():
    sync_group_playlist_folders()