from src.services import *


def exit_menu():
    print("Goodbye!")
    exit()


def sync_all_menu():
    """Main sync function that handles both new followed artists and new saved tracks"""
    print("Starting full sync of new content...")
    
    sync_new_followed_artists()
    
    print("\n" + "="*50 + "\n")
    
    sync_new_saved_tracks_to_playlists()
    
    print("Full sync completed!")


def sync_new_followed_artists_menu():
    sync_new_followed_artists()


def sync_new_saved_tracks_menu():
    sync_new_saved_tracks_to_playlists()


def delete_playlists_by_group_menu():
    group_key = input("Enter the group key: ").strip()
    delete_playlists_by_group(group_key)
