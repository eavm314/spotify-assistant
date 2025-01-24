from sqlalchemy import select
from sqlalchemy.orm import Session

from src.entities import Track
from src.config import engine

def get_last_saved_track():
    query = select(Track).order_by(Track.saved_at.desc()).limit(1)
    with Session(engine) as session:
        result = session.execute(query).scalar_one_or_none()
        return result
    

def save_tracks(tracks):
    with Session(engine) as session:
        session.add_all(tracks)
        session.commit()
    print(f"Added {len(tracks)} tracks to the database.")