from .BaseGroup import BaseGroup, Playlist
from ..artist_service import get_followed_artist_ids

class FollowedArtistGroup(BaseGroup):
    """Artist group that only includes artists that are followed"""
    
    def get_playlist_keys_for_track(self, track) -> list[Playlist]:
        followed_artist_ids = get_followed_artist_ids()
        
        # Only create playlists for artists that are followed
        followed_artists = []
        for artist in track['artists']:
            if artist['id'] in followed_artist_ids:
                followed_artists.append(Playlist(key=artist['id'], name=artist['name']))
        
        return followed_artists
