from datetime import datetime
import pytz
from sqlalchemy import select, insert, update
from sqlalchemy.orm import Session

from src.entities import Artist
from src.config import engine


def get_artist_by_spotify_id(spotify_id):
    """Get artist by Spotify ID"""
    query = select(Artist).where(Artist.spotify_id == spotify_id)
    with Session(engine) as session:
        artist = session.execute(query).scalar_one_or_none()
        return artist


def create_or_update_artist(spotify_id, name, is_followed=False, first_followed_at=None):
    """Create new artist or update existing one"""
    existing_artist = get_artist_by_spotify_id(spotify_id)
    
    with Session(engine) as session:
        if existing_artist:
            # Update existing artist
            if is_followed and not existing_artist.is_followed:
                # Artist was just followed
                query = update(Artist).where(Artist.spotify_id == spotify_id).values(
                    name=name,
                    is_followed=is_followed,
                    first_followed_at=first_followed_at or datetime.now(pytz.utc)
                )
            else:
                query = update(Artist).where(Artist.spotify_id == spotify_id).values(
                    name=name,
                    is_followed=is_followed
                )
            session.execute(query)
            session.commit()
            # Return updated artist
            return get_artist_by_spotify_id(spotify_id)
        else:
            # Create new artist
            query = insert(Artist).values(
                spotify_id=spotify_id,
                name=name,
                is_followed=is_followed,
                first_followed_at=first_followed_at if is_followed else None
            )
            session.execute(query)
            session.commit()
            return get_artist_by_spotify_id(spotify_id)


def get_all_followed_artists():
    """Get all followed artists from database"""
    query = select(Artist).where(Artist.is_followed == True)
    with Session(engine) as session:
        artists = session.execute(query).scalars().all()
        return artists


def get_new_followed_artists():
    """Get artists that are followed but haven't been synced yet"""
    query = select(Artist).where(
        Artist.is_followed == True,
        Artist.last_sync_date.is_(None)
    )
    with Session(engine) as session:
        artists = session.execute(query).scalars().all()
        return artists


def update_artist_sync_date(artist_id):
    """Update the last sync date for an artist"""
    query = update(Artist).where(Artist.id == artist_id).values(
        last_sync_date=datetime.now(pytz.utc)
    )
    with Session(engine) as session:
        session.execute(query)
        session.commit()
