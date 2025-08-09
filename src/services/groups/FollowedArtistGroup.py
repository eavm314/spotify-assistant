from .BaseGroup import BaseGroup, Playlist
from ..artist_service import get_all_followed_artists

class FollowedArtistGroup(BaseGroup):
    """Artist group that only includes artists that are followed"""
    
    def get_playlist_keys_for_track(self, track) -> list[Playlist]:
        followed_artists = get_all_followed_artists()

        # Only create playlists for artists that are followed
        playlists = []
        for artist in track['artists']:
            if artist['id'] in [a.spotify_id for a in followed_artists]:
                playlists.append(Playlist(key=artist['id'], name=artist['name']))

        return playlists
