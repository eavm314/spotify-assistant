from typing import List, Optional
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from .Base import Base

class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    spotify_id: Mapped[str]
    key: Mapped[str] = mapped_column(index=True)
    name: Mapped[str]
    in_folder: Mapped[bool] = mapped_column(default=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("playlist_groups.id"))

    group: Mapped["PlaylistGroup"] = relationship(back_populates="playlists")


class PlaylistGroup(Base):
    __tablename__ = "playlist_groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str]
    name: Mapped[str]
    sync_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    playlists: Mapped[List[Playlist]] = relationship(back_populates="group")