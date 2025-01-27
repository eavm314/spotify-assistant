from .BaseGroup import BaseGroup, Playlist

class ArtistGroup(BaseGroup):
    def get_playlist_keys_for_track(self, track) -> list[Playlist]:
        artists = [Playlist(key=artist['id'], name=artist['name']) for artist in track['artists']]
        return artists