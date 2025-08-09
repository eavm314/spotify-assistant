from .groups import YearGroup, ArtistGroup, FollowedArtistGroup

groups_strategies = {
    'year': YearGroup(),
    'artist': FollowedArtistGroup(),  # Use filtered version for artist groups
    'artist_all': ArtistGroup(),     # Keep original for backward compatibility
}

def get_playlists_to_add(track, group_key):
    strategy = groups_strategies.get(group_key)
    if not strategy:
        raise ValueError(f"Group '{group_key}' strategy not implemented yet")
    
    playlists = strategy.get_playlist_keys_for_track(track)
    return playlists