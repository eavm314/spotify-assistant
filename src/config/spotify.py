import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth


spotify_redirect_uri='http://127.0.0.1:9090'

scope = ['user-library-read', 'playlist-modify-public', 'playlist-modify-private', 'user-follow-read']

# Created empty so other modules can import them at load time;
# init_spotify() must run before any API call.
spotify = spotipy.Spotify()
current_user = {}


def init_spotify():
    """Set up Spotify auth and fetch the current user's profile.

    Raises RuntimeError if credentials are missing, or a spotipy
    error if authentication/the API call fails.
    """
    spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
    spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    missing = [name for name, value in [
        ('SPOTIFY_CLIENT_ID', spotify_client_id),
        ('SPOTIFY_CLIENT_SECRET', spotify_client_secret),
    ] if not value]
    if missing:
        raise RuntimeError(
            f"missing environment variable(s): {', '.join(missing)}. "
            "Copy .env.example to .env and fill in your Spotify API credentials."
        )

    spotify.auth_manager = SpotifyOAuth(
        scope=scope,
        client_id=spotify_client_id,
        client_secret=spotify_client_secret,
        redirect_uri=spotify_redirect_uri,
    )

    current_user.update(spotify.current_user())
    return current_user
