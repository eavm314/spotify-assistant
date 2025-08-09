from .groups import BaseGroup, YearGroup, FollowedArtistGroup

groups_strategies: dict[str, BaseGroup] = {
    'year': YearGroup(),
    'artist': FollowedArtistGroup(),
}

def get_playlists_to_add(track, group_key):
    strategy = groups_strategies.get(group_key)
    if not strategy:
        raise ValueError(f"Group '{group_key}' strategy not implemented yet")
    
    playlists = strategy.get_playlist_keys_for_track(track)
    return playlists