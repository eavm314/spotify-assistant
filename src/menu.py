from src.config import execute_raw_query, spotify
from src.services import *


def exit_menu():
    print("Goodbye!")
    exit()


def sync_playlists_by_group_menu():
    sync_playlists_by_group()
