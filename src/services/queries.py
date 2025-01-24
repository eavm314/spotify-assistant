from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session

from src.entities import Playlist, PlaylistGroup
from src.config import engine


def get_groups():
    query = select(PlaylistGroup)
    with Session(engine) as session:
        groups = session.execute(query).scalars().all()
        return groups


def update_group(group):
    query = update(PlaylistGroup) \
            .where(PlaylistGroup.key == group.key) \
            .values(sync_date=group.sync_date)
    with Session(engine) as session:
        session.execute(query)
        session.commit()


def get_playlist_by_key(key):
    query = select(Playlist).where(Playlist.key == key)
    with Session(engine) as session:
        playlist = session.execute(query).scalar_one_or_none()
        return playlist


def create_playlist(playlist):
    query = insert(Playlist).values(
        key=playlist.key,
        name=playlist.name,
        spotify_id=playlist.spotify_id, 
        group_id=playlist.group_id
    )
    with Session(engine) as session:
        session.execute(query)
        session.commit()


def get_playlists_by_group(group_key):
    query_select = select(Playlist).join(PlaylistGroup).where(PlaylistGroup.key == group_key)
    with Session(engine) as session:
        playlists = session.execute(query_select).scalars().all()
        return playlists


def delete_playlists(group_id):
    query = delete(Playlist).where(Playlist.group_id == group_id)
    with Session(engine) as session:
        session.execute(query)
        session.commit()