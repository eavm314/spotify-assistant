"""
Database initialization script for Spotify Assistant
Run this once to set up the required playlist groups
"""

from datetime import datetime
import pytz
from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from src.entities import PlaylistGroup
from src.config import engine


def init_playlist_groups():
    """Initialize default playlist groups if they don't exist"""
    default_groups = [
        {'key': 'year', 'name': 'Year Groups'},
        {'key': 'artist', 'name': 'Artist Groups'},
    ]
    
    with Session(engine) as session:
        for group_data in default_groups:
            # Check if group already exists
            query = select(PlaylistGroup).where(PlaylistGroup.key == group_data['key'])
            existing_group = session.execute(query).scalar_one_or_none()
            
            if not existing_group:
                # Create new group
                insert_query = insert(PlaylistGroup).values(
                    key=group_data['key'],
                    name=group_data['name'],
                    sync_date=None  # Will be set when first sync happens
                )
                session.execute(insert_query)
                print(f"Created group: {group_data['name']}")
            else:
                print(f"Group already exists: {group_data['name']}")
        
        session.commit()


if __name__ == '__main__':
    print("Initializing database...")
    init_playlist_groups()
    print("Database initialization completed!")
