from datetime import datetime
import pytz

from src.config import spotify
from .queries import get_last_saved_track, save_tracks
from src.entities import Track


def sync_saved_tracks():
    last_saved_track = get_last_saved_track()
    last_sync_date = last_saved_track.sync_date if last_saved_track else None

    tracks_to_add = []

    offset = 0
    end = False
    while True:
        results = spotify.current_user_saved_tracks(limit=50, offset=offset)
        for item in results['items']:
            added_at = datetime.fromisoformat(item['added_at'])
            if last_sync_date != None and added_at <= last_sync_date.replace(tzinfo=pytz.utc):
                end = True
                break
            track = Track(
                name=item['track']['name'],
                spotify_id=item['track']['id'],
                saved_at=added_at
            )
            tracks_to_add.append(track)
        
        if end or not results['next']:
            break

        offset += 50
    
    save_tracks(tracks_to_add)


