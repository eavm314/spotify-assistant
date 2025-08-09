from datetime import datetime

from src.config import spotify, current_user
from .queries import *

cached_tracks = None

def fetch_all_saved_tracks():
    """Get all saved tracks from Spotify API"""
    global cached_tracks
    if cached_tracks:
        return cached_tracks

    print('Fetching saved tracks from Spotify API...')
    offset = 0

    tracks = []
    while True:
        results = spotify.current_user_saved_tracks(limit=50, offset=offset)
        
        for item in results['items']:
            track = item['track']
            added_at = datetime.fromisoformat(item['added_at'])
            
            tracks.append({
                'track': track,
                'added_at': added_at
            })
        
        if not results['next']:
            break
        offset += 50
    
    print(f"Found {len(tracks)} saved tracks")
    cached_tracks = tracks
    return tracks

cached_artists = None

def fetch_all_followed_artists():
    """Fetch all followed artists from Spotify API"""
    global cached_artists
    if cached_artists:
        return cached_artists

    print('Fetching followed artists from Spotify API...')
    followed_artists = []
    current_followed_ids = set()
    
    # Get followed artists from Spotify
    results = spotify.current_user_followed_artists(limit=50)
    while results:
        for artist in results['artists']['items']:
            followed_artists.append(artist)
            current_followed_ids.add(artist['id'])
            
        if results['artists']['next']:
            results = spotify.next(results['artists'])
        else:
            break

    cached_artists = followed_artists
    return followed_artists
