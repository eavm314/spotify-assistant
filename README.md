# Spotify Assistant - Enhanced Version

A Python application that automatically manages Spotify playlists based on your followed artists and saved tracks, with intelligent syncing and state management.

## Features

### 🎵 Smart Artist Tracking
- **Automatic Detection**: Detects new followed artists and creates dedicated playlists
- **Filtered Management**: Only includes tracks by followed artists in artist playlists
- **Cleanup**: Removes tracks from playlists when they're removed from saved tracks
- **State Tracking**: Avoids duplicate work by tracking sync status

### 📅 Playlist Organization
- **Artist Playlists**: Individual playlists for each followed artist with all your saved tracks by them
- **Year Playlists**: Organizes all saved tracks by release year
- **Filtered Artist Groups**: Creates artist playlists but only for artists you follow

### 🔄 Intelligent Syncing
- **Date-based Filtering**: Uses `saved_at` date to efficiently fetch only new content
- **No Track Storage**: Doesn't store track data to avoid database bloat (important for 1000+ tracks)
- **Deletion Sync**: Automatically removes tracks from playlists when unsaved
- **Minimal API Calls**: Efficient fetching and batching to respect Spotify API limits

## Setup

### Prerequisites
- Python 3.8+
- Spotify Developer Account with Client ID and Secret

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
Create a `.env` file with:
```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
DB_URL=sqlite:///spotifyapp.db
```

3. **Initialize the database:**
```bash
python init_db.py
```

4. **Run the application:**
```bash
python main.py
```

## Menu Options

1. **Sync All (New Content)** - Complete sync process:
   - Syncs new followed artists and creates their playlists
   - Adds new saved tracks to existing playlists (filtered appropriately)
   - Removes deleted tracks from managed playlists

2. **Sync playlists by group (Legacy)** - Original functionality

3. **Sync new followed artists** - Creates playlists only for newly followed artists

4. **Sync new saved tracks to playlists** - Adds only new saved tracks to playlists

5. **Sync playlist deletions** - Removes tracks that are no longer saved

6. **Delete playlists by group** - Remove all playlists from a specific group

## How It Works

### State Management
The application uses SQLite to track:
- **Artists**: Follow status, sync dates, first followed date
- **Playlist Groups**: Categories like 'year', 'artist', 'artist_playlists' with sync dates
- **Playlists**: Generated playlists with keys and group associations

**No track storage**: Tracks are filtered by `saved_at` date directly from Spotify API to avoid storing 1000+ records.

### Sync Process

**New Followed Artists:**
1. Fetches current followed artists and updates database
2. Detects newly followed artists (not previously synced)
3. Creates "{Artist Name} - Saved Tracks" playlist for each
4. Searches all saved tracks for tracks by that artist and adds them
5. Marks artist as synced

**New Saved Tracks:**
1. For each playlist group, fetches tracks since last sync date
2. Filters by group type:
   - Year groups: All new tracks
   - Artist groups: Only tracks by followed artists
3. Groups tracks by target playlist and adds them in batches
4. Updates group sync date

**Deleted Tracks:**
1. Gets current saved tracks and existing playlist contents
2. Identifies tracks in playlists but no longer saved
3. Removes those tracks from managed playlists

### API Efficiency
- **Date Filtering**: Only fetches tracks since last sync
- **Batch Operations**: Respects 100-track API limits
- **Follow Status Caching**: Tracks artist follows to minimize API calls
- **Incremental Processing**: Only handles changes since last run

## Technical Architecture

### Key Components
- **Entities**: SQLAlchemy models (Artist, Playlist, PlaylistGroup)
- **Services**: Business logic (enhanced_sync, artist_service, queries)
- **Groups**: Strategy pattern for different playlist types
- **State Management**: Tracks sync progress to enable incremental updates

### Database Schema
- **artists**: Follow tracking with sync dates
- **playlist_groups**: Grouping strategies with last sync dates
- **playlists**: Generated playlists with keys and metadata

### Extensibility
Add new grouping strategies by:
1. Creating new class inheriting from `BaseGroup`
2. Implementing `get_playlist_keys_for_track()` method
3. Adding to `groups_strategies` in `manager.py`

## Troubleshooting

### Common Issues
- **Auth Error**: Verify Spotify credentials in `.env`
- **Database Error**: Run `python init_db.py`
- **Rate Limits**: App handles automatically, but large libraries take time

### Output
Detailed console logs show:
- Artists/tracks processed
- Playlists created/updated
- Tracks added/removed
- Sync completion status
