from typing import List, Optional
from sqlalchemy import ForeignKey, String, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from .Base import Base
from .Playlist import Playlist


class PlaylistTrack(Base):
    __tablename__ = "playlists_tracks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id"))
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id"))
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    spotify_id: Mapped[str]
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sync_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )