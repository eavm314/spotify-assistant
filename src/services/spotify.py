from datetime import datetime
import pytz

from src.config import spotify, current_user
from src.entities import Playlist
from .queries import *
from .manager import get_playlists_to_add


def get_saved_tracks(until=None):
    print('Fetching saved tracks...')
    tracks = []
    offset = 0
    end = False
    while True:
        results = spotify.current_user_saved_tracks(limit=50, offset=offset)
        for item in results['items']:
            added_at = datetime.fromisoformat(item['added_at'])
            if until != None and added_at < until.replace(tzinfo=pytz.utc):
                end = True
                break
            tracks.append(item['track'])

        if end or not results['next']:
            break

        offset += 50

    print(f"Found {len(tracks)} saved tracks")
    return tracks


def sync_playlists_by_group():
    groups = get_groups()
    if len(groups) == 0:
        print("No groups to sync")
        return
    for group in groups:
        print(f"Syncing group '{group.key}'...")
        tracks = get_saved_tracks(until=group.sync_date)
        to_add = {}
        for track in tracks:
            playlists = get_playlists_to_add(track, group.key)
            for playlist in playlists:
                if playlist not in to_add:
                    to_add[playlist] = []
                to_add[playlist].append(track['uri'])
        sorted_items = sorted(to_add.items(), key=lambda x: len(x[1]))
        for playlist, track_uris in sorted_items:
            add_to_playlist(group, playlist, track_uris)

        group.sync_date = datetime.now(pytz.utc)
        update_group(group)
        print(f"Group '{group.key}' synced")


def add_to_playlist(group, playlist_dto, track_uris):
    playlist = get_or_create_playlist(group, playlist_dto)
    total = len(track_uris)
    while len(track_uris) > 0:
        tracks_to_add = track_uris[-100:]
        spotify.playlist_add_items(playlist.spotify_id, tracks_to_add, position=0)
        track_uris = track_uris[:-100]
    print(f"Added {total} tracks to playlist '{playlist.name}'")


def get_or_create_playlist(group, playlist_dto):
    playlist = get_playlist_by_key(playlist_dto.key)
    if playlist:
        return playlist

    new_playlist = spotify.user_playlist_create(
        current_user['id'], playlist_dto.name,
        description=f"Playlist generated by group '{
            group.key}' with key '{playlist_dto.key}'"
    )

    new_playlist = Playlist(
        spotify_id=new_playlist['id'],
        key=playlist_dto.key,
        name=playlist_dto.name,
        group_id=group.id
    )

    create_playlist(new_playlist)
    print(f"Playlist '{new_playlist.name}' created")
    return new_playlist


def delete_playlists_by_group(group_key):
    print("Deleting playlists...")
    playlists = get_playlists_by_group(group_key)
    for playlist in playlists:
        spotify.current_user_unfollow_playlist(playlist.spotify_id)
        print(f"Playlist '{playlist.name}' deleted")

    if len(playlists) > 0:
        delete_playlists(playlists[0].group_id)