from .BaseGroup import BaseGroup, Playlist
from datetime import datetime

class YearGroup(BaseGroup):
    def get_playlist_keys_for_track(self, track) -> list[Playlist]:
        if track['album']['release_date_precision'] == 'year':
            year = int(track['album']['release_date'])
        else:
            year = datetime.fromisoformat(track['album']['release_date']).year
        if year < 2010:
            return [Playlist(key='olds', name='before 2010s')]
        return [Playlist(key=str(year), name=str(year))]