from datetime import datetime
import pytz

from src.config import spotify, current_user
from src.entities import Playlist
from .queries import *
from .spotify import *
from .artist_service import *
from .manager import get_playlists_to_add


def sync_followed_artists():
    """Update local database with followed artists"""
    print('Updating followed artists database...')
    followed_artists = fetch_all_followed_artists()

    for artist in followed_artists:

        # Update or create artist in database
        create_or_update_artist(
            spotify_id=artist['id'],
            name=artist['name'],
            is_followed=True,
            first_followed_at=datetime.now(pytz.utc)
        )

    return followed_artists


def get_saved_tracks_since(since_date):
    """Get saved tracks since last sync date"""
    tracks = fetch_all_saved_tracks()
    if not since_date:
        return tracks
    new_tracks = []
    for track in tracks:
        if track['added_at'] < since_date.replace(tzinfo=pytz.utc):
            print(f"Found {len(new_tracks)} new saved tracks")
            return new_tracks

        new_tracks.append(track)

    print(f"Found {len(new_tracks)} saved tracks")
    return new_tracks


def sync_new_followed_artists():
    """Create playlists for new followed artists and add their tracks from saved tracks"""
    print("Syncing new followed artists...")
    
    # First, fetch and update all followed artists
    sync_followed_artists()
    
    # Get artists that haven't been synced yet
    new_artists = get_new_followed_artists()
    if not new_artists:
        print("No new followed artists to sync")
        return
    
    print(f"Found {len(new_artists)} new followed artists")
    
    # Get all saved tracks (no date filter for new artist playlists)
    all_saved_tracks = fetch_all_saved_tracks()
    
    artist_group = get_group_by_key('artist')
    # For each new artist, create playlist and add their tracks
    for artist in new_artists:
        print(f"Processing artist: {artist.name}")
        
        # Find tracks by this artist in saved tracks
        artist_tracks = []
        for track_item in all_saved_tracks:
            track = track_item['track']
            for track_artist in track['artists']:
                if track_artist['id'] == artist.spotify_id:
                    artist_tracks.append(track['uri'])
                    break
        
        if artist_tracks:
            # Create or get artist playlist
            playlist_dto = Playlist(key=artist.spotify_id, name=artist.name)

            add_to_playlist(artist_group, playlist_dto, artist_tracks)
            print(f"Added {len(artist_tracks)} tracks to {artist.name}'s playlist")
        else:
            print(f"No saved tracks found for {artist.name}")
        
        # Mark artist as synced
        update_artist_sync_date(artist.id)


def sync_new_saved_tracks_to_playlists():
    """Add new saved tracks to year and artist playlists, but only for followed artists"""
    print("Syncing new saved tracks to playlists...")
    
    # Get all groups (year, artist, etc.)
    groups = get_groups()
    if not groups:
        print("No groups configured for syncing")
        return
    
    for group in groups:
        print(f"Syncing group '{group.key}'...")
        
        # Get new tracks since last sync
        new_tracks = get_saved_tracks_since(since_date=group.sync_date)
        
        if not new_tracks:
            print(f"No new tracks for group '{group.key}'")
            continue

        to_add = {}
        for item in new_tracks:
            track = item['track']
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
    """Add tracks to a playlist (enhanced version)"""
    playlist = get_or_create_playlist(group, playlist_dto)
    total = len(track_uris)
    
    if total == 0:
        return
    
    # Add tracks in batches of 100 (Spotify API limit)
    while len(track_uris) > 0:
        tracks_to_add = track_uris[-100:]
        spotify.playlist_add_items(playlist.spotify_id, tracks_to_add, position=0)
        track_uris = track_uris[:-100]
    
    print(f"Added {total} tracks to playlist '{playlist.name}'")


def get_or_create_playlist(group, playlist_dto):
    """Get existing playlist or create new one"""
    playlist = get_playlist_by_key(playlist_dto.key)
    if playlist:
        return playlist

    new_playlist = spotify.user_playlist_create(
        current_user['id'], 
        playlist_dto.name,
        description=f"Playlist generated by group '{group.key}' with key '{playlist_dto.key}'"
    )

    new_playlist_entity = Playlist(
        spotify_id=new_playlist['id'],
        key=playlist_dto.key,
        name=playlist_dto.name,
        group_id=group.id
    )

    create_playlist(new_playlist_entity)
    print(f"Playlist '{new_playlist_entity.name}' created")
    return new_playlist_entity


def delete_playlists_by_group(group_key):
    print("Deleting playlists...")
    playlists = get_playlists_by_group(group_key)
    for playlist in playlists:
        spotify.current_user_unfollow_playlist(playlist.spotify_id)
        print(f"Playlist '{playlist.name}' deleted")

    if len(playlists) > 0:
        delete_playlists(playlists[0].group_id)