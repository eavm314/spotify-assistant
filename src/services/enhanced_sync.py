from datetime import datetime
import pytz
from typing import Set, List, Dict

from src.config import spotify, current_user
from src.entities import Playlist
from .queries import *
from .artist_service import *
from .manager import get_playlists_to_add


def fetch_and_sync_followed_artists():
    """Fetch all followed artists from Spotify API and update local database"""
    print('Fetching followed artists...')
    followed_artists = []
    current_followed_ids = set()
    
    # Get followed artists from Spotify
    results = spotify.current_user_followed_artists(limit=50)
    while results:
        for artist in results['artists']['items']:
            followed_artists.append(artist)
            current_followed_ids.add(artist['id'])
            
            # Update or create artist in database
            create_or_update_artist(
                spotify_id=artist['id'],
                name=artist['name'],
                is_followed=True,
                first_followed_at=datetime.now(pytz.utc)
            )
        
        if results['artists']['next']:
            results = spotify.next(results['artists'])
        else:
            break
    
    # Mark artists as unfollowed if they're no longer in the followed list
    unfollowed_count = mark_artists_as_unfollowed(current_followed_ids)
    if unfollowed_count > 0:
        print(f"Marked {unfollowed_count} artists as unfollowed")
    
    print(f"Found {len(followed_artists)} followed artists")
    return followed_artists


def get_saved_tracks_since(since_date=None):
    """Get saved tracks from Spotify API, optionally filtering by date"""
    print('Fetching saved tracks...')
    tracks = []
    offset = 0
    
    while True:
        results = spotify.current_user_saved_tracks(limit=50, offset=offset)
        
        for item in results['items']:
            track = item['track']
            added_at = datetime.fromisoformat(item['added_at'])
            
            # If we have a since_date and this track is older, we can stop
            if since_date and added_at < since_date.replace(tzinfo=pytz.utc):
                print(f"Found {len(tracks)} new saved tracks")
                return tracks
            
            tracks.append({
                'track': track,
                'added_at': added_at
            })
        
        if not results['next']:
            break
        offset += 50
    
    print(f"Found {len(tracks)} saved tracks")
    return tracks


def get_current_playlist_tracks(playlist_id):
    """Get all tracks currently in a playlist"""
    current_tracks = set()
    results = spotify.playlist_tracks(playlist_id)
    
    while results:
        for item in results['items']:
            if item['track'] and item['track']['id']:
                current_tracks.add(item['track']['id'])
        
        if results['next']:
            results = spotify.next(results)
        else:
            break
    
    return current_tracks


def remove_tracks_from_playlist(playlist_id, track_uris_to_remove):
    """Remove tracks from playlist in batches"""
    if not track_uris_to_remove:
        return
    
    # Remove in batches of 100 (Spotify API limit)
    while track_uris_to_remove:
        batch = track_uris_to_remove[:100]
        track_uris_to_remove = track_uris_to_remove[100:]
        spotify.playlist_remove_all_occurrences_of_items(playlist_id, batch)


def sync_new_followed_artists():
    """Create playlists for new followed artists and add their tracks from saved tracks"""
    print("Syncing new followed artists...")
    
    # First, fetch and update all followed artists
    fetch_and_sync_followed_artists()
    
    # Get artists that haven't been synced yet
    new_artists = get_new_followed_artists()
    if not new_artists:
        print("No new followed artists to sync")
        return
    
    print(f"Found {len(new_artists)} new followed artists")
    
    # Get all saved tracks (no date filter for new artist playlists)
    all_saved_tracks = get_saved_tracks_since()
    
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
            playlist_dto = type('PlaylistDTO', (), {
                'key': f"artist_{artist.spotify_id}",
                'name': f"{artist.name} - Saved Tracks"
            })()
            
            # Create a dummy group for artist playlists
            artist_group = type('Group', (), {
                'id': 0,  # Special ID for artist playlists
                'key': 'artist_playlists',
                'name': 'Artist Playlists'
            })()
            
            add_to_playlist(artist_group, playlist_dto, artist_tracks)
            print(f"Added {len(artist_tracks)} tracks to {artist.name}'s playlist")
        else:
            print(f"No saved tracks found for {artist.name}")
        
        # Mark artist as synced
        update_artist_sync_date(artist.id)


def sync_new_saved_tracks_to_playlists():
    """Add new saved tracks to year and artist playlists, but only for followed artists"""
    print("Syncing new saved tracks to playlists...")
    
    # Get followed artist IDs for filtering
    followed_artist_ids = get_followed_artist_ids()
    
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
        
        tracks_to_process = []
        
        # Filter tracks to only include those by followed artists (for artist groups)
        # or all tracks (for other groups like year)
        for track_item in new_tracks:
            track = track_item['track']
            
            if group.key == 'artist':
                # For artist groups, only include tracks by followed artists
                track_has_followed_artist = any(
                    artist['id'] in followed_artist_ids 
                    for artist in track['artists']
                )
                if track_has_followed_artist:
                    tracks_to_process.append(track)
            else:
                # For other groups (like year), include all tracks
                tracks_to_process.append(track)
        
        if not tracks_to_process:
            print(f"No tracks to process for group '{group.key}' (after filtering)")
            continue
        
        # Group tracks by playlist
        tracks_by_playlist = {}
        for track in tracks_to_process:
            playlists = get_playlists_to_add(track, group.key)
            for playlist_dto in playlists:
                if playlist_dto.key not in tracks_by_playlist:
                    tracks_by_playlist[playlist_dto.key] = {
                        'playlist_dto': playlist_dto,
                        'tracks': []
                    }
                tracks_by_playlist[playlist_dto.key]['tracks'].append(track['uri'])
        
        # Add tracks to playlists
        sorted_playlists = sorted(tracks_by_playlist.items(), key=lambda x: len(x[1]['tracks']))
        for playlist_key, playlist_data in sorted_playlists:
            add_to_playlist(group, playlist_data['playlist_dto'], playlist_data['tracks'])
        
        # Update group sync date
        group.sync_date = datetime.now(pytz.utc)
        update_group(group)
        print(f"Group '{group.key}' synced with {len(tracks_to_process)} tracks")


def sync_playlist_deletions():
    """Remove tracks from playlists that are no longer in saved tracks"""
    print("Syncing playlist deletions...")
    
    # Get all current saved track IDs
    current_saved_tracks = set()
    saved_tracks = get_saved_tracks_since()
    for track_item in saved_tracks:
        current_saved_tracks.add(track_item['track']['id'])
    
    # Get all playlists managed by the system
    all_playlists = []
    groups = get_groups()
    for group in groups:
        playlists = get_playlists_by_group(group.key)
        all_playlists.extend(playlists)
    
    # Check each playlist and remove tracks that are no longer saved
    for playlist in all_playlists:
        print(f"Checking playlist: {playlist.name}")
        
        # Get current tracks in the playlist
        current_playlist_tracks = get_current_playlist_tracks(playlist.spotify_id)
        
        # Find tracks to remove (tracks in playlist but not in saved tracks)
        tracks_to_remove = []
        for track_id in current_playlist_tracks:
            if track_id not in current_saved_tracks:
                tracks_to_remove.append(f"spotify:track:{track_id}")
        
        if tracks_to_remove:
            print(f"Removing {len(tracks_to_remove)} tracks from playlist: {playlist.name}")
            remove_tracks_from_playlist(playlist.spotify_id, tracks_to_remove)
        else:
            print(f"No tracks to remove from playlist: {playlist.name}")


def sync_all_new_content():
    """Main sync function that handles both new followed artists and new saved tracks"""
    print("Starting full sync of new content...")
    
    # First sync new followed artists
    sync_new_followed_artists()
    
    print("\n" + "="*50 + "\n")
    
    # Then sync new saved tracks to existing playlists
    sync_new_saved_tracks_to_playlists()
    
    print("\n" + "="*50 + "\n")
    
    # Finally, remove tracks that are no longer saved
    sync_playlist_deletions()
    
    print("Full sync completed!")


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

    # Handle special case for artist playlists (group.id = 0)
    if group.id == 0:
        # Create artist playlist group if it doesn't exist
        from sqlalchemy import select, insert
        from sqlalchemy.orm import Session
        from src.entities import PlaylistGroup
        from src.config import engine
        
        with Session(engine) as session:
            # Check if artist playlist group exists
            query = select(PlaylistGroup).where(PlaylistGroup.key == 'artist_playlists')
            existing_group = session.execute(query).scalar_one_or_none()
            
            if not existing_group:
                # Create artist playlist group
                insert_query = insert(PlaylistGroup).values(
                    key='artist_playlists',
                    name='Artist Playlists',
                    sync_date=datetime.now(pytz.utc)
                )
                session.execute(insert_query)
                session.commit()
                
                # Get the created group
                existing_group = session.execute(query).scalar_one()
            
            group.id = existing_group.id

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
