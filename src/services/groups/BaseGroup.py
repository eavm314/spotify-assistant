import abc
from collections import namedtuple

Playlist = namedtuple('Playlist', ['key', 'name'])

class BaseGroup:
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def get_playlist_keys_for_track(self, track) -> list[Playlist]:
        '''Return a list of playlists keys to add the track'''
        return
    