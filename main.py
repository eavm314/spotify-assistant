from src.config import execute_query, spotify
from src.services import sync_saved_tracks

if __name__ == '__main__':
    user = spotify.current_user()
    print(f"Welcome, {user['display_name']}!")

    sync_saved_tracks()