import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth


spotify_client_id=os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')

spotify_redirect_uri='http://localhost:9090'

scope = ['user-library-read', 'playlist-modify-public', 'playlist-modify-private', 'user-follow-read']

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope=scope, 
    client_id=spotify_client_id, 
    client_secret=spotify_client_secret, 
    redirect_uri=spotify_redirect_uri, 
))

current_user = spotify.current_user()