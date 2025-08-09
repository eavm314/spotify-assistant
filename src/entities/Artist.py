from typing import Optional
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from .Base import Base

class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    spotify_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str]
    is_followed: Mapped[bool] = mapped_column(Boolean, default=False)
    first_followed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_sync_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Artist(id='{self.spotify_id}', name='{self.name}', is_followed={self.is_followed})>"
